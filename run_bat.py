import os


folder_path = ".\\batch_files\\fedavg\\csic2010"

for root, dirs, files in os.walk (folder_path):
    for filename in files:
        if filename.endswith(".bat"):
            print(f"Executing .bat file: {os.path.join(root, filename)}")
            os.system(os.path.join(root, filename))
            print('\n\n')
        # os.system(os.path.join(folder_path, filename))