      "use strict";

      const DATA_ROOT_CANDIDATES = [
        "./FINALS-PROJECT/processed/",
        "./processed/",
        "../processed/",
      ];
      const MAX_SCATTER_LEGIT_POINTS = 24000;
      const state = {
        overview: null,
        distributions: null,
        samplePoints: null,
        metrics: null,
        activeDataRoot: null,
        liftDeciles: [],
        thresholdProfile: [],
        recommendedThresholdIndex: 0,
        selectedThresholdIndex: 0,
        featureGapAll: [],
        featureTopN: 10,
        showLegit: true,
        showFraud: true,
        scatterPreviewCount: 0,
        browser: {
          search: "",
          classFilter: "all",
          sort: "indexAsc",
          pageSize: 50,
          page: 1,
          filteredCount: 0,
        },
      };

      const charts = {};

      const numberFmt = new Intl.NumberFormat("en-US");
      const moneyFmt = new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
      const percentFmt = new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3,
      });

      function clamp(value, min, max) {
        return Math.min(max, Math.max(min, value));
      }

      function setStatus(text, isError = false) {
        const el = document.getElementById("loadStatus");
        el.textContent = text;
        el.style.color = isError ? "#9f2c0f" : "var(--ink-soft)";
      }

      function setDataStamp(text) {
        const el = document.getElementById("dataStamp");
        if (el) {
          el.textContent = text;
        }
      }

      function formatGeneratedAt(isoString) {
        if (!isoString) {
          return "unknown";
        }
        const parsed = new Date(isoString);
        if (Number.isNaN(parsed.getTime())) {
          return isoString;
        }
        return parsed.toLocaleString();
      }

      function closeAllHelpPopovers(exceptContainer = null) {
        document.querySelectorAll(".help-container").forEach((container) => {
          if (exceptContainer && container === exceptContainer) {
            return;
          }
          const button = container.querySelector(".help-tip");
          const popover = container.querySelector(".help-popover");
          if (button) {
            button.setAttribute("aria-expanded", "false");
          }
          if (popover) {
            popover.hidden = true;
          }
          container.classList.remove("help-open");
        });
      }

      function initHelpTooltips() {
        const containers = document.querySelectorAll(
          ".help-container[data-help-title][data-help-text]",
        );

        containers.forEach((container) => {
          const title = container.getAttribute("data-help-title") || "Help";
          const text = container.getAttribute("data-help-text") || "";

          let button = container.querySelector(":scope > .help-tip");
          if (!button) {
            button = document.createElement("button");
            button.type = "button";
            button.className = "help-tip";
            button.textContent = "?";
            container.appendChild(button);
          }

          button.setAttribute("aria-label", `About ${title}`);
          button.setAttribute("aria-expanded", "false");

          let popover = container.querySelector(":scope > .help-popover");
          if (!popover) {
            popover = document.createElement("div");
            popover.className = "help-popover";
            popover.hidden = true;
            popover.innerHTML = `
              <button type="button" class="help-popover-close" aria-label="Close help">x</button>
              <h4></h4>
              <p></p>
            `;
            container.appendChild(popover);
          }

          const heading = popover.querySelector("h4");
          const body = popover.querySelector("p");
          if (heading) {
            heading.textContent = title;
          }
          if (body) {
            body.textContent = text;
          }

          button.addEventListener("click", (event) => {
            event.stopPropagation();
            const willOpen = popover.hidden;
            closeAllHelpPopovers(container);
            popover.hidden = !willOpen;
            button.setAttribute("aria-expanded", willOpen ? "true" : "false");
            container.classList.toggle("help-open", willOpen);
          });

          const closeBtn = popover.querySelector(".help-popover-close");
          if (closeBtn) {
            closeBtn.addEventListener("click", (event) => {
              event.stopPropagation();
              popover.hidden = true;
              button.setAttribute("aria-expanded", "false");
              container.classList.remove("help-open");
            });
          }

          popover.addEventListener("click", (event) => {
            event.stopPropagation();
          });
        });

        document.addEventListener("click", () => {
          closeAllHelpPopovers();
        });

        document.addEventListener("keydown", (event) => {
          if (event.key === "Escape") {
            closeAllHelpPopovers();
          }
        });
      }

      async function fetchJson(filename, dataRoot, cacheBust) {
        const baseUrl = new URL(dataRoot, window.location.href);
        const resourceUrl = new URL(filename, baseUrl);
        resourceUrl.searchParams.set("v", String(cacheBust));
        const response = await fetch(resourceUrl.href, { cache: "no-store" });
        if (!response.ok) {
          throw new Error(`Failed to load ${filename} (${response.status})`);
        }
        return response.json();
      }

      async function loadBundleForRoot(dataRoot, cacheBust) {
        const [overview, distributions, samplePoints, metrics] =
          await Promise.all([
            fetchJson("overview.json", dataRoot, cacheBust),
            fetchJson("distributions.json", dataRoot, cacheBust),
            fetchJson("sample_points.json", dataRoot, cacheBust),
            fetchJson("metrics.json", dataRoot, cacheBust),
          ]);

        return { overview, distributions, samplePoints, metrics, dataRoot };
      }

      async function tryLoadBundle(cacheBust) {
        const failures = [];

        for (const dataRoot of DATA_ROOT_CANDIDATES) {
          try {
            return await loadBundleForRoot(dataRoot, cacheBust);
          } catch (error) {
            failures.push(`${dataRoot}: ${error.message}`);
          }
        }

        throw new Error(`Could not load from any known data path. ${failures.join(" | ")}`);
      }

      function destroyChart(id) {
        if (charts[id]) {
          charts[id].destroy();
        }
      }

      function basePlugins() {
        return {
          legend: {
            labels: {
              color: "#576560",
              font: { family: "DM Sans", size: 11 },
            },
          },
          tooltip: {
            backgroundColor: "#1f2b2a",
            titleColor: "#f4efe5",
            bodyColor: "#f4efe5",
            borderColor: "#4b5c58",
            borderWidth: 1,
            titleFont: { family: "DM Sans", weight: "700" },
            bodyFont: { family: "DM Sans" },
          },
        };
      }

      function chartScales() {
        return {
          x: {
            ticks: { color: "#576560", font: { family: "DM Sans", size: 10 } },
            grid: { color: "rgba(87,101,96,0.18)" },
          },
          y: {
            ticks: { color: "#576560", font: { family: "DM Sans", size: 10 } },
            grid: { color: "rgba(87,101,96,0.18)" },
          },
        };
      }

      function formatTxId(index) {
        return `TX-${String(index + 1).padStart(6, "0")}`;
      }

      function getAllPoints() {
        return Array.isArray(state.samplePoints?.points)
          ? state.samplePoints.points
          : [];
      }

      function getFraudThreshold() {
        return Number(state.metrics?.best_f1_threshold ?? 0);
      }

      function getAlertLabel(point) {
        return Number(point.score_hint || 0) >= getFraudThreshold()
          ? "Alert"
          : "Below";
      }

      function getClassLabel(point) {
        return point.class === 1 ? "Fraud" : "Legitimate";
      }

      function thinLegitimatePoints(points, maxPoints) {
        if (points.length <= maxPoints) {
          return points;
        }

        const stride = Math.ceil(points.length / maxPoints);
        const preview = [];
        for (let index = 0; index < points.length; index += stride) {
          preview.push(points[index]);
        }
        return preview.slice(0, maxPoints);
      }

      function buildLoadedStatus() {
        const points = getAllPoints();
        const legitTotal = Number(
          state.samplePoints?.metadata?.legit_sample_size ?? 0,
        );
        const fraudTotal = Number(
          state.samplePoints?.metadata?.fraud_sample_size ?? 0,
        );
        const previewNote =
          legitTotal > MAX_SCATTER_LEGIT_POINTS
            ? ` Scatter preview shows all ${numberFmt.format(fraudTotal)} fraud points plus ${numberFmt.format(state.scatterPreviewCount)} legitimate points for responsiveness.`
            : "";

        return `Loaded ${numberFmt.format(points.length)} processed transactions successfully.${previewNote}`;
      }

      function filterDataset(legitValues, fraudValues) {
        const datasets = [];
        if (state.showLegit) {
          datasets.push({
            label: "Legitimate",
            values: legitValues,
            color: "rgba(27,122,105,0.75)",
            border: "#1b7a69",
          });
        }
        if (state.showFraud) {
          datasets.push({
            label: "Fraud",
            values: fraudValues,
            color: "rgba(217,90,44,0.78)",
            border: "#d95a2c",
          });
        }
        return datasets;
      }

      function renderKpis() {
        const o = state.overview;
        const m = state.metrics;

        document.getElementById("kpiTotal").textContent = numberFmt.format(
          o.total_transactions,
        );
        document.getElementById("kpiFraud").textContent = numberFmt.format(
          o.fraud_transactions,
        );
        document.getElementById("kpiFraudRate").textContent =
          `${percentFmt.format(o.fraud_rate_pct)}% of all transactions`;
        document.getElementById("kpiAuprc").textContent = m.auprc.toFixed(4);
        document.getElementById("kpiBaseline").textContent =
          `Baseline PR: ${(m.baseline_positive_rate * 100).toFixed(3)}%`;
        document.getElementById("kpiThreshold").textContent =
          m.best_f1_threshold.toFixed(3);
        document.getElementById("kpiBestF1").textContent =
          `Best F1: ${m.best_f1.toFixed(4)}`;

        setDataStamp(
          `Data version: ${formatGeneratedAt(o.generated_at)} (${state.activeDataRoot || "unknown path"})`,
        );
      }

      function renderClassChart() {
        destroyChart("classChart");
        const ctx = document.getElementById("classChart");
        const labels = ["Legitimate", "Fraud"];
        const values = [
          state.overview.legit_transactions,
          state.overview.fraud_transactions,
        ];

        charts.classChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels,
            datasets: [
              {
                label: "Transaction count",
                data: values,
                backgroundColor: [
                  "rgba(27,122,105,0.75)",
                  "rgba(217,90,44,0.78)",
                ],
                borderColor: ["#1b7a69", "#d95a2c"],
                borderWidth: 1,
                borderRadius: 10,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: basePlugins(),
            scales: {
              ...chartScales(),
              y: {
                type: "logarithmic",
                ticks: {
                  color: "#576560",
                  callback: (value) => numberFmt.format(value),
                },
                grid: { color: "rgba(87,101,96,0.18)" },
              },
            },
          },
        });
      }

      function renderAmountChart() {
        destroyChart("amountChart");
        const ctx = document.getElementById("amountChart");
        const bins = state.distributions.amount_bins;
        const labels = bins.map((b) => b.label);

        const dataSets = filterDataset(
          bins.map((b) => b.legit_count),
          bins.map((b) => b.fraud_count),
        ).map((d) => ({
          label: d.label,
          data: d.values,
          borderColor: d.border,
          backgroundColor: d.color,
          borderWidth: 2,
          fill: false,
          tension: 0.25,
          pointRadius: 2,
        }));

        charts.amountChart = new Chart(ctx, {
          type: "line",
          data: { labels, datasets: dataSets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: basePlugins(),
            scales: {
              ...chartScales(),
              y: {
                type: "logarithmic",
                ticks: {
                  color: "#576560",
                  callback: (v) => numberFmt.format(v),
                },
                grid: { color: "rgba(87,101,96,0.18)" },
              },
            },
          },
        });
      }

      function renderHourChart() {
        destroyChart("hourChart");
        const ctx = document.getElementById("hourChart");
        const hourly = state.distributions.hourly;
        const labels = hourly.map((x) => `${x.hour}:00`);
        const legitTotal = hourly.reduce((sum, row) => sum + row.legit_count, 0);
        const fraudTotal = hourly.reduce((sum, row) => sum + row.fraud_count, 0);
        const legitPct = hourly.map((row) =>
          legitTotal ? (row.legit_count / legitTotal) * 100 : 0,
        );
        const fraudPct = hourly.map((row) =>
          fraudTotal ? (row.fraud_count / fraudTotal) * 100 : 0,
        );

        const dataSets = filterDataset(
          legitPct,
          fraudPct,
        ).map((d) => ({
          label:
            d.label === "Fraud"
              ? "Fraud (% of fraud daily volume)"
              : "Legitimate (% of legit daily volume)",
          data: d.values,
          borderColor: d.border,
          backgroundColor: d.color,
          borderWidth: 2,
          tension: d.label === "Fraud" ? 0.22 : 0.3,
          pointRadius: d.label === "Fraud" ? 2 : 0,
          fill: false,
          yAxisID: "y",
        }));

        charts.hourChart = new Chart(ctx, {
          type: "line",
          data: { labels, datasets: dataSets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              ...basePlugins(),
              tooltip: {
                ...basePlugins().tooltip,
                callbacks: {
                  label: (item) => {
                    const label = item.dataset.label || "Series";
                    return `${label}: ${Number(item.raw).toFixed(2)}%`;
                  },
                  afterBody: (items) => {
                    const idx = items[0].dataIndex;
                    const row = hourly[idx];
                    const hourTotal = row.legit_count + row.fraud_count;
                    const share = hourTotal
                      ? (row.fraud_count / hourTotal) * 100
                      : 0;
                    return [
                      `Legitimate count: ${numberFmt.format(row.legit_count)}`,
                      `Fraud count: ${numberFmt.format(row.fraud_count)}`,
                      `Fraud share this hour: ${share.toFixed(3)}%`,
                      `Hour total: ${numberFmt.format(hourTotal)}`,
                    ];
                  },
                },
              },
            },
            scales: {
              x: chartScales().x,
              y: {
                type: "linear",
                position: "left",
                min: 0,
                ticks: {
                  color: "#576560",
                  callback: (v) => `${Number(v).toFixed(0)}%`,
                },
                title: {
                  display: true,
                  text: "% of class daily volume",
                  color: "#576560",
                },
                grid: { color: "rgba(87,101,96,0.18)" },
              },
            },
          },
        });
      }

      function renderScatterChart() {
        destroyChart("scatterChart");
        const ctx = document.getElementById("scatterChart");
        const points = getAllPoints();

        const legit = [];
        const fraudScatter = [];
        for (const point of points) {
          if (point.class === 1) {
            fraudScatter.push({ x: point.time_hour, y: point.amount_log10 });
          } else {
            legit.push(point);
          }
        }
        const legitPreview = thinLegitimatePoints(
          legit,
          MAX_SCATTER_LEGIT_POINTS,
        );
        state.scatterPreviewCount = legitPreview.length;

        const legitScatter = legitPreview
          .map((p) => ({ x: p.time_hour, y: p.amount_log10 }));

        const datasets = [];
        if (state.showLegit) {
          datasets.push({
            label:
              legit.length > legitPreview.length
                ? `Legitimate preview (${numberFmt.format(legitPreview.length)} of ${numberFmt.format(legit.length)})`
                : `Legitimate (${numberFmt.format(legit.length)})`,
            data: legitScatter,
            pointRadius: 2,
            pointHoverRadius: 3,
            borderWidth: 0,
            backgroundColor: "rgba(27,122,105,0.25)",
          });
        }
        if (state.showFraud) {
          datasets.push({
            label: `Fraud (${numberFmt.format(fraudScatter.length)})`,
            data: fraudScatter,
            pointRadius: 4,
            pointHoverRadius: 5,
            borderWidth: 0,
            backgroundColor: "rgba(217,90,44,0.75)",
          });
        }

        charts.scatterChart = new Chart(ctx, {
          type: "scatter",
          data: { datasets },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: basePlugins(),
            scales: {
              ...chartScales(),
              x: {
                ...chartScales().x,
                title: { display: true, text: "Hour of day", color: "#576560" },
                min: 0,
                max: 24,
              },
              y: {
                ...chartScales().y,
                title: {
                  display: true,
                  text: "log10(Amount + 1)",
                  color: "#576560",
                },
              },
            },
          },
        });
      }

      function renderRecordBrowser() {
        const tbody = document.getElementById("recordTableBody");
        const summary = document.getElementById("browserSummary");
        const meta = document.getElementById("recordMeta");
        const pageLabel = document.getElementById("recordPageLabel");
        const prevButton = document.getElementById("recordPrev");
        const nextButton = document.getElementById("recordNext");
        const points = getAllPoints();

        if (!tbody || !summary || !meta || !pageLabel || !prevButton || !nextButton) {
          return;
        }

        if (points.length === 0) {
          tbody.innerHTML =
            '<tr><td colspan="7">No processed records loaded.</td></tr>';
          summary.textContent = "No processed records available.";
          meta.textContent = "Browser unavailable";
          pageLabel.textContent = "Page 0 of 0";
          prevButton.disabled = true;
          nextButton.disabled = true;
          return;
        }

        const search = state.browser.search.trim().toLowerCase();
        let rows = points.map((_, index) => index);

        if (state.browser.classFilter === "fraud") {
          rows = rows.filter((index) => points[index].class === 1);
        } else if (state.browser.classFilter === "legit") {
          rows = rows.filter((index) => points[index].class === 0);
        }

        if (search) {
          rows = rows.filter((index) => {
            const point = points[index];
            const txId = formatTxId(index).toLowerCase();
            const classLabel = getClassLabel(point).toLowerCase();
            const alertLabel = getAlertLabel(point).toLowerCase();
            return (
              txId.includes(search) ||
              classLabel.includes(search) ||
              alertLabel.includes(search)
            );
          });
        }

        switch (state.browser.sort) {
          case "scoreDesc":
            rows.sort((a, b) => points[b].score_hint - points[a].score_hint);
            break;
          case "scoreAsc":
            rows.sort((a, b) => points[a].score_hint - points[b].score_hint);
            break;
          case "amountDesc":
            rows.sort((a, b) => points[b].amount - points[a].amount);
            break;
          case "amountAsc":
            rows.sort((a, b) => points[a].amount - points[b].amount);
            break;
          case "hourAsc":
            rows.sort((a, b) => points[a].time_hour - points[b].time_hour);
            break;
          case "hourDesc":
            rows.sort((a, b) => points[b].time_hour - points[a].time_hour);
            break;
          default:
            rows.sort((a, b) => a - b);
            break;
        }

        state.browser.filteredCount = rows.length;
        const pageSize = Math.max(1, Number(state.browser.pageSize) || 50);
        const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
        state.browser.page = clamp(state.browser.page, 1, totalPages);

        const startIndex = (state.browser.page - 1) * pageSize;
        const pageRows = rows.slice(startIndex, startIndex + pageSize);

        tbody.innerHTML = pageRows.length
          ? pageRows
              .map((index) => {
                const point = points[index];
                const classLabel = getClassLabel(point);
                const classClass =
                  point.class === 1 ? "class-fraud" : "class-legit";
                const alertLabel = getAlertLabel(point);
                const alertClass =
                  alertLabel === "Alert" ? "alert-yes" : "alert-no";

                return `
                  <tr>
                    <td class="tx-id">${formatTxId(index)}</td>
                    <td><span class="class-chip ${classClass}">${classLabel}</span></td>
                    <td>${Number(point.time_hour).toFixed(2)}</td>
                    <td>$${moneyFmt.format(Number(point.amount || 0))}</td>
                    <td>${Number(point.amount_log10 || 0).toFixed(4)}</td>
                    <td>${Number(point.score_hint || 0).toFixed(4)}</td>
                    <td><span class="alert-chip ${alertClass}">${alertLabel}</span></td>
                  </tr>
                `;
              })
              .join("")
          : '<tr><td colspan="7">No records match the current browser filters.</td></tr>';

        const shownStart = rows.length === 0 ? 0 : startIndex + 1;
        const shownEnd = Math.min(startIndex + pageRows.length, rows.length);
        summary.textContent =
          `Loaded ${numberFmt.format(points.length)} full processed transactions. Showing ${numberFmt.format(shownStart)}-${numberFmt.format(shownEnd)} of ${numberFmt.format(rows.length)} matching records.`;
        meta.textContent =
          `Best-F1 alert threshold: ${getFraudThreshold().toFixed(4)} | Fraud rows: ${numberFmt.format(Number(state.samplePoints?.metadata?.fraud_sample_size ?? state.overview?.fraud_transactions ?? 0))} | Legitimate rows: ${numberFmt.format(Number(state.samplePoints?.metadata?.legit_sample_size ?? state.overview?.legit_transactions ?? 0))}`;
        pageLabel.textContent = `Page ${state.browser.page} of ${totalPages}`;
        prevButton.disabled = state.browser.page <= 1;
        nextButton.disabled = state.browser.page >= totalPages;
      }

      function renderPRChart() {
        destroyChart("prChart");
        const ctx = document.getElementById("prChart");
        const curve = state.metrics.pr_curve;

        charts.prChart = new Chart(ctx, {
          type: "line",
          data: {
            datasets: [
              {
                label: "Heuristic Precision-Recall",
                data: curve.map((p) => ({ x: p.recall, y: p.precision })),
                borderColor: "#d95a2c",
                backgroundColor: "rgba(217,90,44,0.25)",
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.15,
                parsing: false,
              },
              {
                label: "Baseline precision",
                data: [
                  { x: 0, y: state.metrics.baseline_positive_rate },
                  { x: 1, y: state.metrics.baseline_positive_rate },
                ],
                borderColor: "#4d7ea8",
                borderWidth: 1.5,
                borderDash: [7, 6],
                pointRadius: 0,
                parsing: false,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: basePlugins(),
            scales: {
              x: {
                type: "linear",
                min: 0,
                max: 1,
                title: { display: true, text: "Recall", color: "#576560" },
                ticks: { color: "#576560" },
                grid: { color: "rgba(87,101,96,0.18)" },
              },
              y: {
                min: 0,
                max: 1,
                title: { display: true, text: "Precision", color: "#576560" },
                ticks: { color: "#576560" },
                grid: { color: "rgba(87,101,96,0.18)" },
              },
            },
          },
        });
      }

      function renderLiftChart() {
        destroyChart("liftChart");
        const deciles = state.liftDeciles;
        if (!deciles || deciles.length === 0) {
          return;
        }

        const ctx = document.getElementById("liftChart");
        const labels = deciles.map((d) => `D${d.decile}`);
        const fraudRatePct = deciles.map((d) => d.fraud_rate * 100);
        const cumulativeCapturePct = deciles.map(
          (d) => d.cumulative_fraud_captured * 100,
        );
        const liftVsBaseline = deciles.map((d) => d.lift_vs_baseline);

        charts.liftChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels,
            datasets: [
              {
                type: "bar",
                label: "Fraud Rate per Decile (%)",
                data: fraudRatePct,
                backgroundColor: "rgba(217,90,44,0.68)",
                borderColor: "#d95a2c",
                borderWidth: 1,
                yAxisID: "y",
              },
              {
                type: "line",
                label: "Cumulative Fraud Captured (%)",
                data: cumulativeCapturePct,
                borderColor: "#1b7a69",
                backgroundColor: "rgba(27,122,105,0.2)",
                pointRadius: 3,
                tension: 0.25,
                yAxisID: "y",
              },
              {
                type: "line",
                label: "Lift vs Baseline",
                data: liftVsBaseline,
                borderColor: "#4d7ea8",
                borderDash: [6, 4],
                pointRadius: 2,
                tension: 0,
                yAxisID: "y1",
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              ...basePlugins(),
              tooltip: {
                ...basePlugins().tooltip,
                callbacks: {
                  label: (item) => {
                    const label = item.dataset.label || "Series";
                    const value = Number(item.raw);
                    return `${label}: ${value.toFixed(4)}`;
                  },
                  afterBody: (items) => {
                    const idx = items[0].dataIndex;
                    const decile = deciles[idx];
                    return [
                      `Fraud count: ${numberFmt.format(decile.fraud_count)}`,
                      `Decile fraud rate: ${(decile.fraud_rate * 100).toFixed(3)}%`,
                      `Captured by this point: ${(decile.cumulative_fraud_captured * 100).toFixed(2)}%`,
                      `Lift: ${decile.lift_vs_baseline.toFixed(2)}x`,
                    ];
                  },
                },
              },
            },
            scales: {
              x: chartScales().x,
              y: {
                position: "left",
                title: {
                  display: true,
                  text: "%",
                  color: "#576560",
                },
                ticks: { color: "#576560" },
                grid: { color: "rgba(87,101,96,0.18)" },
              },
              y1: {
                position: "right",
                title: {
                  display: true,
                  text: "Lift x",
                  color: "#576560",
                },
                ticks: { color: "#576560" },
                grid: { drawOnChartArea: false },
              },
            },
          },
        });
      }

      function populateFeatureOptions() {
        const select = document.getElementById("featureTopN");
        if (!select || !state.featureGapAll.length) {
          return;
        }

        if (select.options.length === 0) {
          const maxN = state.featureGapAll.length;
          const optionValues = [5, 10, 15, 20, 28]
            .filter((n) => n <= maxN)
            .concat(maxN)
            .filter((value, index, arr) => arr.indexOf(value) === index)
            .sort((a, b) => a - b);

          optionValues.forEach((value) => {
            const option = document.createElement("option");
            option.value = String(value);
            option.textContent = String(value);
            select.appendChild(option);
          });
        }

        state.featureTopN = clamp(
          state.featureTopN,
          1,
          state.featureGapAll.length,
        );
        select.value = String(state.featureTopN);
      }

      function renderFeatureChart() {
        destroyChart("featureChart");
        if (!state.featureGapAll || state.featureGapAll.length === 0) {
          return;
        }

        const topN = clamp(state.featureTopN, 1, state.featureGapAll.length);
        const rows = [...state.featureGapAll]
          .sort((a, b) => b.abs_gap - a.abs_gap)
          .slice(0, topN)
          .reverse();

        const ctx = document.getElementById("featureChart");

        charts.featureChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels: rows.map((row) => row.feature),
            datasets: [
              {
                label: "Legit Mean",
                data: rows.map((row) => row.legit_mean),
                backgroundColor: "rgba(27,122,105,0.7)",
                borderColor: "#1b7a69",
                borderWidth: 1,
              },
              {
                label: "Fraud Mean",
                data: rows.map((row) => row.fraud_mean),
                backgroundColor: "rgba(217,90,44,0.72)",
                borderColor: "#d95a2c",
                borderWidth: 1,
              },
            ],
          },
          options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              ...basePlugins(),
              tooltip: {
                ...basePlugins().tooltip,
                callbacks: {
                  label: (item) => {
                    const label = item.dataset.label || "Mean";
                    const value = item.parsed.x;
                    return `${label}: ${value.toFixed(4)}`;
                  },
                  afterBody: (items) => {
                    const idx = items[0].dataIndex;
                    const row = rows[idx];
                    return [`Absolute gap: ${row.abs_gap.toFixed(4)}`];
                  },
                },
              },
            },
            scales: {
              x: {
                ...chartScales().x,
                title: {
                  display: true,
                  text: "Average transformed feature value",
                  color: "#576560",
                },
              },
              y: chartScales().y,
            },
          },
        });
      }

      function updateMetricsPanel(snapshot) {
        document.getElementById("cmTp").textContent = numberFmt.format(
          snapshot.tp,
        );
        document.getElementById("cmFp").textContent = numberFmt.format(
          snapshot.fp,
        );
        document.getElementById("cmTn").textContent = numberFmt.format(
          snapshot.tn,
        );
        document.getElementById("cmFn").textContent = numberFmt.format(
          snapshot.fn,
        );

        const entries = [
          ["Precision", snapshot.precision],
          ["Recall", snapshot.recall],
          ["Specificity", snapshot.specificity],
          ["False Positive Rate", snapshot.fpr],
          ["Accuracy", snapshot.accuracy],
          ["F1", snapshot.f1],
        ];

        document.getElementById("rateList").innerHTML = entries
          .map(
            ([label, value]) =>
              `<li><b>${label}:</b> ${(value * 100).toFixed(3)}%</li>`,
          )
          .join("");
      }

      function initThresholdSimulator() {
        const slider = document.getElementById("thresholdSlider");
        const info = document.getElementById("thresholdInfo");
        if (!slider || !info) {
          return;
        }

        if (state.thresholdProfile.length === 0) {
          slider.disabled = true;
          slider.value = "0";
          info.textContent = "Threshold simulator unavailable";
          return;
        }

        slider.disabled = false;
        slider.min = "0";
        slider.max = String(state.thresholdProfile.length - 1);
        slider.step = "1";

        state.recommendedThresholdIndex = clamp(
          state.recommendedThresholdIndex,
          0,
          state.thresholdProfile.length - 1,
        );
        state.selectedThresholdIndex = clamp(
          state.selectedThresholdIndex,
          0,
          state.thresholdProfile.length - 1,
        );
        slider.value = String(state.selectedThresholdIndex);
      }

      function renderThresholdSnapshot() {
        const info = document.getElementById("thresholdInfo");

        if (!state.thresholdProfile || state.thresholdProfile.length === 0) {
          const fallback = {
            ...state.metrics.confusion_matrix,
            ...state.metrics.rates,
            f1: state.metrics.best_f1,
          };
          updateMetricsPanel(fallback);
          if (info) {
            info.textContent = `Threshold: ${state.metrics.best_f1_threshold.toFixed(4)} (best F1)`;
          }
          return;
        }

        state.selectedThresholdIndex = clamp(
          state.selectedThresholdIndex,
          0,
          state.thresholdProfile.length - 1,
        );
        const point = state.thresholdProfile[state.selectedThresholdIndex];
        const slider = document.getElementById("thresholdSlider");
        if (slider) {
          slider.value = String(state.selectedThresholdIndex);
        }

        updateMetricsPanel(point);
        if (info) {
          const bestTag =
            state.selectedThresholdIndex === state.recommendedThresholdIndex
              ? " (best F1)"
              : "";
          info.textContent = `Threshold: ${point.threshold.toFixed(4)}${bestTag}`;
        }
      }

      function renderInsights() {
        const o = state.overview;
        const m = state.metrics;
        const corr = o.amount_score_correlation;
        const strongerThanBaseline = (
          m.auprc / m.baseline_positive_rate
        ).toFixed(1);
        const topDecileCapture =
          state.liftDeciles && state.liftDeciles.length > 0
            ? (state.liftDeciles[0].cumulative_fraud_captured * 100).toFixed(2)
            : null;

        const narrative = [
          `Fraud appears in <b>${o.fraud_rate_pct.toFixed(3)}%</b> of transactions, which confirms the dataset is severely imbalanced and unsuitable for plain accuracy scoring.`,
          `The heuristic ranking reaches an <b>AUPRC of ${m.auprc.toFixed(4)}</b>, about <b>${strongerThanBaseline}x</b> above baseline precision (${(m.baseline_positive_rate * 100).toFixed(3)}%).`,
          `At the best-F1 threshold (<b>${m.best_f1_threshold.toFixed(3)}</b>), the model tradeoff captures fraud with recall <b>${(m.rates.recall * 100).toFixed(2)}%</b> while controlling false positives through specificity <b>${(m.rates.specificity * 100).toFixed(2)}%</b>.`,
          topDecileCapture
            ? `Top decile concentration is strong: the highest-risk 10% captures <b>${topDecileCapture}%</b> of known fraud cases.`
            : "",
          `Amount-to-score correlation is <b>${corr.toFixed(3)}</b>, indicating that amount alone is only one component and PCA features contribute strongly to separation.`,
        ]
          .filter(Boolean)
          .join(" ");

        document.getElementById("insightText").innerHTML = narrative;
      }

      function renderAll() {
        if (
          !state.overview ||
          !state.distributions ||
          !state.samplePoints ||
          !state.metrics
        ) {
          return;
        }

        renderKpis();
        renderClassChart();
        renderAmountChart();
        renderHourChart();
        renderScatterChart();
        renderPRChart();
        renderLiftChart();
        renderFeatureChart();
        renderThresholdSnapshot();
        renderRecordBrowser();
        renderInsights();
        setStatus(buildLoadedStatus());
      }

      async function loadData(forceRefresh = false) {
        setStatus(
          "Loading overview, distributions, full processed points, and metrics...",
        );
        try {
          const cacheBust = forceRefresh ? Date.now() : Date.now();
          const loaded = await tryLoadBundle(cacheBust);

          const { overview, distributions, samplePoints, metrics, dataRoot } =
            loaded;

          state.overview = overview;
          state.distributions = distributions;
          state.samplePoints = samplePoints;
          state.metrics = metrics;
          state.activeDataRoot = dataRoot;

          state.liftDeciles = Array.isArray(metrics?.lift?.deciles)
            ? metrics.lift.deciles
            : [];
          state.thresholdProfile = Array.isArray(
            metrics?.threshold_profile?.points,
          )
            ? metrics.threshold_profile.points
            : [];
          state.recommendedThresholdIndex = clamp(
            Number(metrics?.threshold_profile?.recommended_index ?? 0),
            0,
            Math.max(0, state.thresholdProfile.length - 1),
          );
          state.selectedThresholdIndex = state.recommendedThresholdIndex;

          state.featureGapAll = Array.isArray(distributions?.feature_gap_all)
            ? distributions.feature_gap_all
            : Array.isArray(distributions?.feature_gap_top10)
              ? distributions.feature_gap_top10
              : [];
          state.featureTopN = Math.min(
            10,
            Math.max(1, state.featureGapAll.length || 1),
          );

          populateFeatureOptions();
          initThresholdSimulator();
          renderAll();
        } catch (error) {
          console.error(error);
          setDataStamp("Data version: unavailable");
          setStatus(
            "Could not load processed data. Run FINALS-PROJECT/preprocess_creditcard.py, commit FINALS-PROJECT/processed/*.json, and reload this page.",
            true,
          );
        }
      }

      function bindControls() {
        document
          .getElementById("toggleLegit")
          .addEventListener("change", (event) => {
            state.showLegit = event.target.checked;
            renderAll();
          });
        document
          .getElementById("toggleFraud")
          .addEventListener("change", (event) => {
            state.showFraud = event.target.checked;
            renderAll();
          });

        const recordSearch = document.getElementById("recordSearch");
        if (recordSearch) {
          recordSearch.addEventListener("input", (event) => {
            state.browser.search = event.target.value;
            state.browser.page = 1;
            renderRecordBrowser();
          });
        }

        const recordClassFilter = document.getElementById("recordClassFilter");
        if (recordClassFilter) {
          recordClassFilter.addEventListener("change", (event) => {
            state.browser.classFilter = event.target.value;
            state.browser.page = 1;
            renderRecordBrowser();
          });
        }

        const recordSort = document.getElementById("recordSort");
        if (recordSort) {
          recordSort.addEventListener("change", (event) => {
            state.browser.sort = event.target.value;
            state.browser.page = 1;
            renderRecordBrowser();
          });
        }

        const recordPageSize = document.getElementById("recordPageSize");
        if (recordPageSize) {
          recordPageSize.addEventListener("change", (event) => {
            state.browser.pageSize = Number(event.target.value);
            state.browser.page = 1;
            renderRecordBrowser();
          });
        }

        const recordReset = document.getElementById("recordReset");
        if (recordReset) {
          recordReset.addEventListener("click", () => {
            state.browser.search = "";
            state.browser.classFilter = "all";
            state.browser.sort = "indexAsc";
            state.browser.pageSize = 50;
            state.browser.page = 1;

            const searchInput = document.getElementById("recordSearch");
            const classSelect = document.getElementById("recordClassFilter");
            const sortSelect = document.getElementById("recordSort");
            const pageSizeSelect = document.getElementById("recordPageSize");
            if (searchInput) searchInput.value = "";
            if (classSelect) classSelect.value = "all";
            if (sortSelect) sortSelect.value = "indexAsc";
            if (pageSizeSelect) pageSizeSelect.value = "50";

            renderRecordBrowser();
          });
        }

        const recordPrev = document.getElementById("recordPrev");
        if (recordPrev) {
          recordPrev.addEventListener("click", () => {
            state.browser.page = Math.max(1, state.browser.page - 1);
            renderRecordBrowser();
          });
        }

        const recordNext = document.getElementById("recordNext");
        if (recordNext) {
          recordNext.addEventListener("click", () => {
            state.browser.page += 1;
            renderRecordBrowser();
          });
        }

        const featureSelect = document.getElementById("featureTopN");
        if (featureSelect) {
          featureSelect.addEventListener("change", (event) => {
            state.featureTopN = Number(event.target.value);
            renderFeatureChart();
          });
        }

        const thresholdSlider = document.getElementById("thresholdSlider");
        if (thresholdSlider) {
          thresholdSlider.addEventListener("input", (event) => {
            state.selectedThresholdIndex = Number(event.target.value);
            renderThresholdSnapshot();
          });
        }

        const refreshButton = document.getElementById("refreshData");
        if (refreshButton) {
          refreshButton.addEventListener("click", () => {
            loadData(true);
          });
        }
      }

      document.addEventListener("DOMContentLoaded", () => {
        initHelpTooltips();
        bindControls();
        loadData();
      });
    
