class Component:
    def __init__(self, name, inputMax = 100, inputLevel=1, ConfHW=1, performance_decrease=20, performance_increase=25,
                 base_value=1):
        self.name = name
        self.inputMax = inputMax
        self.inputLevel = inputLevel
        self.ConfHW = ConfHW
        self.performance_decrease = performance_decrease / 100
        self.performance_increase = performance_increase / 100
        self.base_value = base_value
        self.matrix = self.create_matrix()

    def create_matrix(self):
        matrix = [[0 for _ in range(self.ConfHW)] for _ in range(self.inputLevel)]

        matrix[0][0] = self.base_value

        # Fill the first row
        for j in range(1, self.ConfHW):
            matrix[0][j] = round(matrix[0][j - 1] / (1 + self.performance_increase), 9)

        # Fill the first column
        for i in range(1, self.inputLevel):
            matrix[i][0] = round(matrix[i - 1][0] * (1 + self.performance_decrease), 9)

        # Fill the remaining part
        for i in range(1, self.inputLevel):
            for j in range(1, self.ConfHW):
                matrix[i][j] = round(matrix[i][j - 1] / (1 + self.performance_increase), 9)

        return matrix

    def get_matrix(self):
        for row in self.matrix:
            print(row)

