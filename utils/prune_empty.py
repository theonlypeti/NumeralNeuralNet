import pandas as pd


def prune_empty(file_path):
    # Load the data from the CSV file
    dataset = pd.read_csv(file_path)

    # Apply the mask to filter the data
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    mask = ~(X == 0).all(axis=1)
    X = X[mask]
    y = y[mask]

    # Create a DataFrame from the filtered data
    filtered_data = pd.DataFrame(X)
    filtered_data['target'] = y

    # Write the filtered data back to the CSV file
    filtered_data.to_csv(file_path, index=False)
    return filtered_data

