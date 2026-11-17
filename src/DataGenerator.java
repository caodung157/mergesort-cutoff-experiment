import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class DataGenerator {
    private static final long SEED = 42L;

    public static void main(String[] args) throws IOException {
        int[] sizes = {10_000, 50_000, 100_000, 500_000, 1_000_000};
        String[] types = {"random", "nearly_sorted", "reverse", "duplicates"};

        for (int n : sizes) {
            for (String type : types) {
                int[] arr = generateArray(n, type);
                String fileName = String.format("data/%s_%d.txt", type, n);
                saveToFile(arr, fileName);
                System.out.println("Đã tạo: " + fileName);
            }
        }
    }

    private static int[] generateArray(int n, String type) {
        Random rand = new Random(SEED);
        int[] arr = new int[n];

        switch (type) {
            case "random":
                for (int i = 0; i < n; i++) arr[i] = rand.nextInt();
                break;

            case "nearly_sorted":
                for (int i = 0; i < n; i++) arr[i] = i;
                // Hoán đổi ngẫu nhiên 1% số phần tử
                int swaps = Math.max(1, n / 100);
                for (int s = 0; s < swaps; s++) {
                    int idx1 = rand.nextInt(n);
                    int idx2 = rand.nextInt(n);
                    int tmp = arr[idx1];
                    arr[idx1] = arr[idx2];
                    arr[idx2] = tmp;
                }
                break;

            case "reverse":
                for (int i = 0; i < n; i++) arr[i] = n - i;
                break;

            case "duplicates":
                for (int i = 0; i < n; i++) arr[i] = rand.nextInt(10);
                break;
        }
        return arr;
    }

    private static void saveToFile(int[] arr, String fileName) throws IOException {
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(fileName))) {
            bw.write(Integer.toString(arr.length));
            bw.newLine();
            for (int val : arr) {
                bw.write(Integer.toString(val));
                bw.newLine();
            }
        }
    }
}