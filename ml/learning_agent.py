import os
import json
import torch
import torch.nn as nn
import torch.optim as optim

# A dummy neural network model for demonstration.
class DummyModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DummyModel, self).__init__()
        self.fc = nn.Linear(input_dim, output_dim)
    
    def forward(self, x):
        return self.fc(x)

def load_feedback(feedback_path):
    data = []
    if os.path.exists(feedback_path):
        with open(feedback_path, 'r') as f:
            for line in f:
                try:
                    feedback = json.loads(line.strip())
                    data.append(feedback)
                except Exception as e:
                    print(f"Error decoding feedback: {e}")
    return data

def train():
    feedback_file = os.path.join(os.getcwd(), 'logs', 'feedback.log')
    feedback_data = load_feedback(feedback_file)
    
    if not feedback_data:
        print("No feedback data available for training.")
        return
    
    # For demonstration, assume feedback contains "features" (a list of floats) and "reward" (a float).
    X = []
    y = []
    for item in feedback_data:
        features = item.get("features", [0.0, 0.0, 0.0])
        reward = item.get("reward", 0.0)
        X.append(features)
        y.append([reward])
    
    # Convert data to tensors.
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    
    # Instantiate the dummy model.
    model = DummyModel(input_dim=X_tensor.shape[1], output_dim=1)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    # Training loop.
    epochs = 50
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_tensor)
        loss = criterion(outputs, y_tensor)
        loss.backward()
        optimizer.step()
        if (epoch+1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
    
    # Save the trained model.
    torch.save(model.state_dict(), os.path.join('ml', 'dummy_model.pth'))
    print("Model training completed and saved.")

if __name__ == "__main__":
    train()
