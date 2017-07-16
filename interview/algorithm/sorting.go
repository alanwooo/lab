//go run sorting.go
package main

import "fmt"

func MaoPao(arr [18]int) [18]int {
	l := len(arr)
	for i := 0; i < l; i++ {
		for j := 0; j < l-i-1; j++ {
			if arr[j] < arr[j+1] {
				arr[j], arr[j+1] = arr[j+1], arr[j]
			}
		}
	}
	//fmt.Println(arr)
	return arr
}

func MarPao1(arr [18]int) [18]int {
	var l int = len(arr)
	for i := 1; i < l; i++ {
		for j := i - 1; j >= 0 && arr[j] < arr[j+1]; j-- {
			arr[j], arr[j+1] = arr[j+1], arr[j]
		}
	}
	return arr
}

func XuanZhe(arr [18]int) [18]int {
	var l int = len(arr)
	var max int
	for i := 0; i < l; i++ {
		max = i
		for j := i + 1; j < l; j++ {
			if arr[max] < arr[j] {
				//arr[i], arr[j] = arr[j], arr[i]
				max = j
			}
		}
		arr[i], arr[max] = arr[max], arr[i]
	}
	//fmt.Println(arr)
	return arr
}

// ChaRu with MaoPao
func ChaRu(arr [18]int) [18]int {
	var l int = len(arr)
	for i := 1; i < l; i++ {
		for j := 0; j < i; j++ {
			if arr[j] < arr[i] {
				for z := i; z > j; z-- {
					// MaoPao to switch the value
					arr[z], arr[z-1] = arr[z-1], arr[z]
				}
			}
		}
	}
	return arr
}

func ChaRu1(arr [18]int) [18]int {
	var l int = len(arr)
	for i := 1; i < l; i++ {
		for j := 0; j < i; j++ {
			if arr[j] > arr[i] {
				continue
			}
			// This is ChaRu, move the value back, then insert the tmp value
			var tmp int = arr[i]
			for z := i; z > j; z-- {
				arr[z] = arr[z-1]
			}
			arr[j] = tmp
		}
	}
	return arr
}

func ChaRu2(arr [18]int) [18]int {
	var l int = len(arr)
	for i := 1; i < l; i++ {
		if arr[i] < arr[i-1] {
			continue
		}
		var tmp int = arr[i]
		var j int = i
		for ; j > 0 && arr[j-1] < tmp; j-- {
			arr[j] = arr[j-1]
		}
		arr[j] = tmp
	}
	return arr
}

func ChaRu3(arr [18]int) [18]int {
	var l int = len(arr)
	for i := 1; i < l; i++ {
		var tmp int = arr[i]
		var j int = i - 1
		for ; j >= 0; j-- {
			if tmp < arr[j] {
				break
			}
			arr[j+1] = arr[j]
		}
		arr[j+1] = tmp
	}
	return arr
}

func XiEr(arr [18]int) [18]int {
	var l int = len(arr)
	for gap := l / 2; gap > 0; gap /= 2 {
		for i := gap; i < l; i++ {
			var j, tmp int = 0, arr[i]
			for j = i - gap; j >= 0 && arr[j] < tmp; j -= gap {
				arr[j+gap] = arr[j]
			}
			arr[j+gap] = tmp
		}
	}
	return arr
}

func KuaiShu(arr []int, l, r int) {
	if l < r {
		var i, j, tmp int
		i, j, tmp = l, r, arr[l]
		for {
			for ; j > i; j-- {
				if tmp <= arr[j] {
					arr[i] = arr[j]
					i += 1
					break
				}
			}
			for ; i < j; i++ {
				if tmp > arr[i] {
					arr[j] = arr[i]
					j -= 1
					break
				}
			}
			if i == j {
				break
			}
		}
		arr[i] = tmp
		//fmt.Println(tmp, arr)
		KuaiShu(arr, l, i-1)
		KuaiShu(arr, i+1, r)
	}
}

func CheckResult(msg string, arr [18]int) {
	var l int = len(arr)
	for i := 0; i < l-1; i++ {
		if arr[i] < arr[i+1] {
			fmt.Println(msg, arr, "ERROR")
			return
		}
	}
	fmt.Println(msg, arr, "")
}

func main() {
	//var arr = [8]int{3, 1, 7, 4, 9, 6, 2, 6}
	var arr = [18]int{113, 11, 7, 4, 9, 6, 2, 6, 10, 23, 8, 54, 12, 34, 23, 7, 79, 11}
	fmt.Println(arr)
	CheckResult("MaoPao:  ", MaoPao(arr))
	CheckResult("XuanZhe: ", XuanZhe(arr))
	CheckResult("ChaRu:   ", ChaRu(arr))
	CheckResult("ChaRu1:  ", ChaRu1(arr))
	CheckResult("ChaRu2:  ", ChaRu2(arr))
	CheckResult("ChaRu3   ", ChaRu3(arr))
	CheckResult("XiEr:    ", XiEr(arr))
	//arr[:] is the address porint
	var arr1 []int = arr[:]
	//copy(arr1, arr[:])
	KuaiShu(arr[:], 0, len(arr)-1)
	fmt.Println("KuaiShu: ", arr)
	fmt.Println(arr)
	fmt.Println(arr1)
}
