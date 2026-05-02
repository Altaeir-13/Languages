import math
import random

#Linear Algebra 
def T(M): return [list(col) for col in zip(*M)]
def dot(A, B): return [[sum(a * b for a, b in zip(r, c)) for c in T(B)] for r in A]
def add(A, b): return [[x + y for x, y in zip(r, b[0])] for r in A]
def sub(A, B): return [[a - b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]
def mul(A, B): return [[a * b for a, b in zip(rA, rB)] for rA, rB in zip(A, B)]
def scale(A, s): return [[x * s for x in r] for r in A]
def col_sum(A): return [[sum(col) for col in T(A)]]

#Activation Functions
def relu(A): return [[max(0.0, x) for x in r] for r in A] # neg = 0 // pos = pos
def derivate_relu(A): return [[1.0 if x > 0 else 0.0 for x in r] for r in A] 
def sigmoid(A): return [[1.0 / (1.0 + math.exp(-max(-500, min(500, x)))) for x in r] for r in A] # vgp ≃ 1 // vgn ≃ 0 

class MinimalMLP:
    #Initialization
    def __init__(self):
        # Layer 1: 2 inputs -> 8 hidden neurons
        self.W1 = [[random.uniform(-1, 1) for _ in range(8)] for _ in range(2)] #weights
        self.b1 = [[0.0] * 8] #biases for each neuron
        # Layer 2: 8 hidden neurons -> 1 output
        self.W2 = [[random.uniform(-1, 1)] for _ in range(8)]
        self.b2 = [[0.0]]

    #Forward Pass // Linear transformation
    def forward(self, X):
        #layer 1
        self.Pre1 = add(dot(X, self.W1), self.b1)
        self.Act1 = relu(self.Pre1)
        #layer 2
        self.Pre2 = add(dot(self.Act1, self.W2), self.b2)
        self.Act2 = sigmoid(self.Pre2)
        return self.Act2 # output probabilities

    #Backpropagation and Training
    def train(self, X, Y, epochs=10000, lr=0.1):
        m = len(X) #number of samples for the XOR problem
        for epoch in range(epochs):
            
            Act2 = self.forward(X)
            dPre2 = sub(Act2, Y)
            gradW2 = scale(dot(T(self.Act1), dPre2), 1/m)
            gradb2 = scale(col_sum(dPre2), 1/m)
            
            dAct1 = dot(dPre2, T(self.W2))
            dPre1 = mul(dAct1, derivate_relu(self.Pre1))
            gradW1 = scale(dot(T(X), dPre1), 1/m)
            gradb1 = scale(col_sum(dPre1), 1/m)
            
            self.W2 = sub(self.W2, scale(gradW2, lr))
            self.b2 = sub(self.b2, scale(gradb2, lr))
            self.W1 = sub(self.W1, scale(gradW1, lr))
            self.b1 = sub(self.b1, scale(gradb1, lr))

            if epoch == 0 or (epoch + 1) % 1000 == 0:
                loss = -sum(y[0] * math.log(max(1e-15, a[0])) + 
                            (1 - y[0]) * math.log(max(1e-15, 1 - a[0])) 
                            for y, a in zip(Y, Act2)) / m
                print(f"Epoch {epoch + 1:5d} | Loss: {loss:.6f}")

    def predict(self, X):
        return [[1 if a[0] >= 0.5 else 0] for a in self.forward(X)]


if __name__ == "__main__":
    X_train = [[0, 0], [0, 1], [1, 0], [1, 1]]
    Y_train = [[0], [1], [1], [0]]
    
    print("Training Minimalist XOR MLP...")
    mlp = MinimalMLP()
    mlp.train(X_train, Y_train)
    
    print("\nResults:")
    for x, y, p, prob in zip(X_train, Y_train, mlp.predict(X_train), mlp.forward(X_train)):
        print(f"Input: {x} | Target: {y[0]} | Prediction: {p[0]} | Probability: {prob[0]:.4f}")