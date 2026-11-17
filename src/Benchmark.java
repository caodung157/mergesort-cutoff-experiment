import java.io.*;
import java.util.Arrays;
import java.util.Locale;

public class Benchmark {
    // Khảo sát dày từ 1..20 (gồm mốc 7 và 10 trong giáo trình) và mở rộng tới 64
    private static final int[] CUTOFFS = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        11, 12, 13, 14, 15, 16, 18, 20, 24, 32, 48, 64
    };

    private static final int WARMUP_RUNS = 15;
    private static final int TRIALS = 25; // Số lần đo lặp lại cho mỗi cấu hình

    public static void main(String[] args) throws IOException {
        int[] sizes = {10_000, 50_000, 100_000, 500_000, 1_000_000};
        String[] types = {"random", "nearly_sorted", "reverse", "duplicates"};

        // 1. Giai đoạn làm nóng JVM (Warm-up)
        System.out.println("Đang làm nóng JVM (Warm-up)...");
        Integer[] warmupData = loadFromFile("data/random_100000.txt");
        for (int w = 0; w < WARMUP_RUNS; w++) {
            for (int c : CUTOFFS) {
                Integer[] copy = Arrays.copyOf(warmupData, warmupData.length);
                Merge.sort(copy, c);
            }
        }

        // 2. Chạy thí nghiệm chính và ghi kết quả thô ra CSV
        String outputCsv = "results/benchmark_raw.csv";
        try (PrintWriter pw = new PrintWriter(new FileWriter(outputCsv))) {
            pw.println("data_type,n,cutoff,trial,time_ms");

            for (String type : types) {
                for (int n : sizes) {
                    String fileName = String.format("data/%s_%d.txt", type, n);
                    Integer[] original = loadFromFile(fileName);
                    System.out.printf("Đang đo: %-14s | N = %d%n", type, n);

                    for (int cutoff : CUTOFFS) {
                        for (int t = 1; t <= TRIALS; t++) {
                            // Sao chép mảng gốc bên ngoài vùng bấm giờ
                            Integer[] work = Arrays.copyOf(original, original.length);

                            long startTime = System.nanoTime();
                            Merge.sort(work, cutoff);
                            long endTime = System.nanoTime();

                            // Kiểm tra tính đúng đắn ở lần chạy đầu tiên
                            if (t == 1 && !Merge.isSorted(work)) {
                                throw new RuntimeException("Lỗi: Mảng chưa được sắp xếp đúng!");
                            }

                            double elapsedMs = (endTime - startTime) / 1_000_000.0;
                            pw.printf(Locale.US, "%s,%d,%d,%d,%.4f%n",
                                      type, n, cutoff, t, elapsedMs);
                        }
                    }
                }
            }
        }
        System.out.println("Hoàn tất! Dữ liệu đo đã lưu tại: " + outputCsv);
    }

    private static Integer[] loadFromFile(String fileName) throws IOException {
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            int n = Integer.parseInt(br.readLine().trim());
            Integer[] arr = new Integer[n];
            for (int i = 0; i < n; i++) {
                arr[i] = Integer.parseInt(br.readLine().trim());
            }
            return arr;
        }
    }
}