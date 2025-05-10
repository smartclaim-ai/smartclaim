import pandas as pd

# Read a sample of the file
sample_size = 10000  # Number of rows to sample
output_filename = "data/minimized_data.csv"

try:
    df = pd.read_csv("data/data.csv")
    sampled_df = df.sample(n=sample_size)
    sampled_df.to_csv(output_filename, index=False)
    print(f"Sampled data ({sample_size} rows) saved to {output_filename}")
except MemoryError:
    print(
        "File is too large to read directly for sampling. Consider chunking or external tools."
    )
