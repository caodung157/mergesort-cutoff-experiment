import os
import pandas as pd
import matplotlib.pyplot as plt

# Kiểm tra tệp dữ liệu đầu vào
RAW_CSV = "results/benchmark_raw.csv"
if not os.path.exists(RAW_CSV):
    raise FileNotFoundError(
        f"Không tìm thấy '{RAW_CSV}'. Hãy chạy Benchmark.java trước và đứng ở thư mục gốc khi chạy script này."
    )

df = pd.read_csv(RAW_CSV)

# ==============================================================================
# 1. THỐNG KÊ CHI TIẾT CHO DỮ LIỆU NGẪU NHIÊN (N = 1,000,000)
# ==============================================================================
sub_1m = df[(df["data_type"] == "random") & (df["n"] == 1_000_000)]
stats_1m = sub_1m.groupby("cutoff")["time_ms"].agg(
    mean="mean",
    std="std",
    median="median",
    min="min"
).reset_index()

base_time = stats_1m.loc[stats_1m["cutoff"] == 1, "mean"].values[0]
stats_1m["speedup_pct"] = (base_time - stats_1m["mean"]) / base_time * 100

# Lưu bảng CSV
stats_1m.to_csv("results/summary_random_1M.csv", index=False)

# Tìm CUTOFF tối ưu
best_row = stats_1m.loc[stats_1m["mean"].idxmin()]
best_cutoff = int(best_row["cutoff"])

print("=== BẢNG THỐNG KÊ (RANDOM, N = 1,000,000) ===")
print(stats_1m.round(3).to_string(index=False))
print(f"\n--> CUTOFF tối ưu trên máy của bạn (Random, N=1M): {best_cutoff} ({best_row['mean']:.2f} ms)")

# ==============================================================================
# 2. TỔNG HỢP CUTOFF TỐI ƯU TRÊN MỌI KÍCH THƯỚC VÀ LOẠI DỮ LIỆU
# ==============================================================================
grouped = df.groupby(["data_type", "n", "cutoff"])["time_ms"].mean().reset_index()
idx_min = grouped.groupby(["data_type", "n"])["time_ms"].idxmin()
optimal_all = grouped.loc[idx_min].rename(columns={"cutoff": "optimal_cutoff", "time_ms": "min_mean_ms"})
optimal_all.to_csv("results/optimal_cutoffs_all.csv", index=False)

print("\n=== TỔNG HỢP CUTOFF TỐI ƯU THEO TỪNG BỘ DỮ LIỆU ===")
print(optimal_all.round(3).to_string(index=False))

# ==============================================================================
# 3. BIỂU ĐỒ 1: ĐƯỜNG CONG CHỮ U (RANDOM, N = 1,000,000) KÈM SAI SỐ +- STD
# ==============================================================================
plt.figure(figsize=(11, 5.5))
plt.errorbar(
    stats_1m["cutoff"], stats_1m["mean"], yerr=stats_1m["std"],
    fmt="-o", color="#1f77b4", ecolor="#aec7e8", elinewidth=1.5, capsize=4,
    label="Thời gian TB ± Độ lệch chuẩn (ms)"
)

plt.axvline(7, color="#ff7f0e", linestyle="--", linewidth=1.5, label="CUTOFF = 7 (Giáo trình cũ)")
plt.axvline(10, color="#2ca02c", linestyle="--", linewidth=1.5, label="CUTOFF = 10 (Giáo trình mới)")
plt.axvline(best_cutoff, color="#d62728", linestyle=":", linewidth=2,
            label=f"CUTOFF tối ưu máy này = {best_cutoff}")

plt.title("Biểu đồ 1: Ảnh hưởng của CUTOFF đến thời gian chạy Mergesort (Random, N = 1,000,000)")
plt.xlabel("Giá trị CUTOFF")
plt.ylabel("Thời gian chạy trung bình (ms)")
plt.xticks(stats_1m["cutoff"], rotation=45)
plt.grid(True, linestyle="--", alpha=0.35)
plt.legend()
plt.tight_layout()
plt.savefig("results/chart1_u_curve_1M.png", dpi=300)
plt.close()

# ==============================================================================
# 4. BIỂU ĐỒ 2: SO SÁNH ĐA KÍCH THƯỚC N (CHUẨN HÓA SO VỚI CUTOFF = 1)
# ==============================================================================
plt.figure(figsize=(11, 5.5))
sizes_to_plot = [50_000, 100_000, 500_000, 1_000_000]

for n in sizes_to_plot:
    sub_n = df[(df["data_type"] == "random") & (df["n"] == n)]
    if sub_n.empty:
        continue
    mean_n = sub_n.groupby("cutoff")["time_ms"].mean().reset_index()
    t1 = mean_n.loc[mean_n["cutoff"] == 1, "time_ms"].values[0]
    mean_n["normalized_time"] = mean_n["time_ms"] / t1  # Tỷ lệ thời gian so với CUTOFF = 1
    plt.plot(mean_n["cutoff"], mean_n["normalized_time"], marker="o", markersize=4, label=f"N = {n:,}")

plt.axhline(1.0, color="gray", linestyle="--", linewidth=1, label="Mốc chuẩn CUTOFF = 1 (100%)")
plt.title("Biểu đồ 2: Tỷ lệ thời gian chạy theo CUTOFF qua các kích thước mảng N (Dữ liệu Random)")
plt.xlabel("Giá trị CUTOFF")
plt.ylabel("Thời gian chuẩn hóa (T_cutoff / T_1)")
plt.xticks(stats_1m["cutoff"], rotation=45)
plt.grid(True, linestyle="--", alpha=0.35)
plt.legend()
plt.tight_layout()
plt.savefig("results/chart2_multi_n.png", dpi=300)
plt.close()

# ==============================================================================
# 5. BIỂU ĐỒ 3: SO SÁNH THEO PHÂN PHỐI DỮ LIỆU (N = 1,000,000)
# ==============================================================================
plt.figure(figsize=(11, 5.5))
type_labels = {
    "random": "Ngẫu nhiên (Random)",
    "nearly_sorted": "Gần như đã sắp xếp (Nearly Sorted)",
    "reverse": "Sắp xếp ngược (Reverse Sorted)",
    "duplicates": "Nhiều trùng lặp (Many Duplicates)"
}

for dtype, label in type_labels.items():
    sub_t = df[(df["data_type"] == dtype) & (df["n"] == 1_000_000)]
    if sub_t.empty:
        continue
    mean_t = sub_t.groupby("cutoff")["time_ms"].mean().reset_index()
    plt.plot(mean_t["cutoff"], mean_t["time_ms"], marker="o", markersize=4, label=label)

plt.title("Biểu đồ 3: Thời gian chạy Mergesort theo CUTOFF trên các loại dữ liệu (N = 1,000,000)")
plt.xlabel("Giá trị CUTOFF")
plt.ylabel("Thời gian chạy trung bình (ms)")
plt.xticks(stats_1m["cutoff"], rotation=45)
plt.grid(True, linestyle="--", alpha=0.35)
plt.legend()
plt.tight_layout()
plt.savefig("results/chart3_data_types.png", dpi=300)
plt.close()

print("\nĐã xuất thành công 2 bảng CSV và 3 biểu đồ PNG vào thư mục 'results/'!")