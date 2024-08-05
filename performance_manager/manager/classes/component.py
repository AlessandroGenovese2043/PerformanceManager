class Component:
    def __init__(self, name, inputMax=100, inputLevel=1, ConfHW=1, performance_decrease=20, performance_increase=25,
                 base_value=1, currentConfHW=0, ):
        self.name = name
        self.inputMax = inputMax
        self.inputLevel = inputLevel
        self.ConfHW = ConfHW
        self.performance_decrease = performance_decrease / 100
        self.performance_increase = performance_increase / 100
        self.base_value = base_value
        self.currentConfHW = currentConfHW
        self.matrix = self.create_matrix()

    def getName(self):
        return self.name
    def getInputMax(self):
        return self.inputMax
    def getConfHW(self):
        return self.ConfHW
    def getInputLevel(self):
        return self.inputLevel
    def getCurrentConfHW(self):
        return self.currentConfHW
    def getPerformanceIncrease(self):
        return self.performance_increase
    def getPerformanceDecrease(self):
        return self.performance_decrease
    def getBaseValue(self):
        return self.base_value

    def setConfHW(self, targetConf):
        if targetConf > 0 & targetConf <= self.ConfHW:
            self.currentConfHW = targetConf
            return 1
        else:
            return -1

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
        return self.matrix

    def get_value_from_matrix(self, inputLevel, confHW=None):
        if confHW is None:
            confHW = self.currentConfHW
        try:
            return self.matrix[inputLevel][confHW]
        except IndexError:
            return None

    def add_row(self):
        new_row = []
        # first value
        value = round(self.matrix[self.inputLevel - 1][0] * (1 + self.performance_decrease), 9)
        new_row.append(value)
        for i in range(1, self.ConfHW):
            value = round(value / (1 + self.performance_increase), 9)
            new_row.append(value)
        self.matrix.append(new_row)
        self.inputLevel += 1
        return new_row

    def add_column(self):
        new_column = []
        # first value
        value = round(self.matrix[0][self.ConfHW-1] / (1 + self.performance_increase), 9)
        new_column.append(value)
        for i in range(1, self.inputLevel):
            value = round(value * (1 + self.performance_decrease), 9)
            new_column.append(value)
        for i in range(len(self.matrix)):
            self.matrix[i].append(new_column[i])
        self.ConfHW += 1
        return new_column



    '''def _format_matrix(self):
        # Format the matrix for better readability
        formatted_matrix = "\n".join(["\t".join(map(str, row)) for row in self.matrix])
        return formatted_matrix'''

    def info(self):
        return (
            f"Component: {self.name}, InputMax: {self.inputMax}, InputLevel: {self.inputLevel}, ConfHW: {self.ConfHW} performance decrease:{self.performance_decrease}, "
            f"performance increase:{self.performance_increase}, base value:{self.base_value}, currentConfHW:{self.currentConfHW}"
            f" Matrix:{self.matrix}")
