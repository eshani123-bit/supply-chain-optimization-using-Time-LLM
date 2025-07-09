from model.predictor import predict_demand

# Test forecast for productA
result = predict_demand('productA')
print(f"Predicted demand for Product A (next 7 days): {result} units")