public class Merge {
    // Trộn hai mảng con đã sắp xếp a[lo..mid] và a[mid+1..hi]
    private static void merge(Comparable[] a, Comparable[] aux, int lo, int mid, int hi) {
        // Chép sang mảng phụ aux[]
        for (int k = lo; k <= hi; k++) {
            aux[k] = a[k];
        }

        // Trộn ngược lại mảng a[]
        int i = lo, j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid)                   a[k] = aux[j++];
            else if (j > hi)               a[k] = aux[i++];
            else if (less(aux[j], aux[i])) a[k] = aux[j++];
            else                           a[k] = aux[i++];
        }
    }

    // Đệ quy chia đôi và dùng Insertion sort khi hi <= lo + cutoff - 1
    private static void sort(Comparable[] a, Comparable[] aux, int lo, int hi, int cutoff) {
        if (hi <= lo + cutoff - 1) {
            Insertion.sort(a, lo, hi);
            return;
        }
        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff);
        sort(a, aux, mid + 1, hi, cutoff);
        merge(a, aux, lo, mid, hi);
    }

    // Hàm giao diện công khai
    public static void sort(Comparable[] a, int cutoff) {
        Comparable[] aux = new Comparable[a.length];
        sort(a, aux, 0, a.length - 1, cutoff);
    }

    private static boolean less(Comparable v, Comparable w) {
        return v.compareTo(w) < 0;
    }

    // Hàm kiểm tra tính đúng đắn sau khi sắp xếp
    public static boolean isSorted(Comparable[] a) {
        for (int i = 1; i < a.length; i++) {
            if (less(a[i], a[i - 1])) return false;
        }
        return true;
    }
}