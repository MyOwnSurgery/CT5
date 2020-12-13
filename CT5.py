import numpy as np
from itertools import combinations


class RMCode:

    def __init__(self, r=2, m=4):
        self.r = r
        self.m = m

        k = 0
        m_factorial = np.math.factorial(m)
        for i in range(r + 1):
            k += m_factorial / np.math.factorial(i) / np.math.factorial(m - i)

        self.k = int(k)
        self.n = 2 ** m

        self.J = self.generate_J()
        self.views = self.generate_binary_views()
        self.matrix = self.generate_matrix()

        self.Z_c = range(self.m)

    @staticmethod
    def count_zeros(arr):
        return arr.count(0)

    @staticmethod
    def xor(a, b):
        if len(a) != len(b):
            raise Exception()
        return [1 if a[j] != b[j] else 0 for j in range(len(a))]

    @staticmethod
    def multiply(a, b):
        if len(a) != len(b):
            raise Exception()
        return [a[i] * b[i] for i in range(len(a))]

    @staticmethod
    def scalar(a, b):
        multiply = RMCode.multiply(a, b)
        sum = 0
        for i in multiply:
            sum ^= i
        return sum

    """5.2"""

    # 5.2.1
    def generate_J(self):
        array = [()]
        key = lambda arr: int(''.join(reversed([str(i) for i in arr])))
        for i in range(1, self.r + 1, 1):
            sorted_list = sorted([j for j in combinations(range(self.m), i)], reverse=True, key=key)
            for j in sorted_list:
                array.append(j)
        return array

    # 5.2.2 helper
    def mapper(self, i):
        bn = ''.join(reversed(list(bin(i)[2:])))
        bn += (self.m - len(bn)) * '0'
        return bn

    # 5.2.2
    def generate_binary_views(self):
        return list(map(self.mapper, range(2 ** self.m)))

    def generate_line_by_j(self, j):
        line = []
        for v in self.views:
            elem = 1
            for i in j:
                if v[i] != '0':
                    elem = 0
                    break
            line.append(elem)
        return line

    # 5.2.3
    def generate_matrix(self):
        matrix = []
        for j in self.J:
            matrix.append(self.generate_line_by_j(j))
        return matrix

    # 5.2.4
    def encode(self, message):
        return np.dot(message, self.matrix) % 2

    """5.3"""

    # 5.3.1.2
    def get_J_c(self, J):
        return tuple(set(self.Z_c) - set(J))

    # 5.3.1.3
    def get_shifts(self, J):
        views = [(list(i)) for i in self.views.copy()]
        for t in views:
            for j in J:
                t[j] = '0'
        views = np.unique(views, axis=0)
        return views

    # 5.3.1.4
    def get_verification_vector(self, J):
        J_c = self.get_J_c(J)
        shifts = self.get_shifts(J)
        res = []
        b = self.generate_line_by_j(J_c)
        for s in shifts:
            b_copy = b.copy()
            shift_value = int(''.join(list(reversed(s))), 2)
            if shift_value != 0:
                b_copy = [0] * shift_value + b_copy[:-shift_value]
            res.append(b_copy)
        return res

    # 5.3.2
    def decode(self, message):
        i = self.r
        J = self.J
        w = message.copy()
        decoded = [0] * self.k
        v_i = [0] * self.n
        for j in range(len(J) - 1, -1, -1):
            J_j = J[j]
            if len(J_j) != i:
                i -= 1
                try:
                    w = RMCode.xor(w, v_i)
                    v_i = [0] * self.n
                except  Exception:
                    pass
            count = 0
            verifications = self.get_verification_vector(J_j)
            for v in verifications:
                count += RMCode.scalar(w, v)
            size_half = len(verifications) // 2
            if count > size_half:
                decoded[j] = 1
                v_i = RMCode.xor(v_i, self.generate_line_by_j(J_j))
            elif count == size_half:
                print("Error can be fixed")
        return decoded


