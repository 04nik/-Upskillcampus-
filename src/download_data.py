import os
import urllib.request
import zipfile
import io

def download_and_extract():
    url = "https://docs.google.com/uc?export=download&id=1y61cDyuO9Zrp1fSchWcAmCxk0B6SMx7X"
    print(f"Downloading dataset from Google Drive: {url}")
    
    # Send a request with a User-Agent header to avoid being blocked
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            zip_bytes = response.read()
        print("Download complete. Extracting files...")
    except Exception as e:
        print(f"Error downloading the file: {e}")
        return False
        
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load the outer zip archive
        outer_zip = zipfile.ZipFile(io.BytesIO(zip_bytes))
        
        # Extract the docx file
        docx_name = "Project9_smart-city-traffic-patterns/Project9_smart-city-traffic-patterns.docx"
        if docx_name in outer_zip.namelist():
            with open(os.path.join("data", "Project9_smart-city-traffic-patterns.docx"), "wb") as f:
                f.write(outer_zip.read(docx_name))
            print("Extracted Word Document.")

        # Load the inner zip archive
        inner_zip_name = "Project9_smart-city-traffic-patterns/Project9_smart-city-traffic-patterns.zip"
        if inner_zip_name in outer_zip.namelist():
            inner_zip_bytes = outer_zip.read(inner_zip_name)
            inner_zip = zipfile.ZipFile(io.BytesIO(inner_zip_bytes))
            
            # Extract train.csv
            train_member = "smart-city-traffic-patterns/train_aWnotuB.csv"
            if train_member in inner_zip.namelist():
                with open(os.path.join("data", "train.csv"), "wb") as f:
                    f.write(inner_zip.read(train_member))
                print("Extracted train.csv -> data/train.csv")
                
            # Extract test.csv
            test_member = "smart-city-traffic-patterns/datasets_8494_11879_test_BdBKkAj.csv"
            if test_member in inner_zip.namelist():
                with open(os.path.join("data", "test.csv"), "wb") as f:
                    f.write(inner_zip.read(test_member))
                print("Extracted test.csv -> data/test.csv")
        
        print("Data extraction completed successfully!")
        return True
    except Exception as e:
        print(f"Error during extraction: {e}")
        return False

if __name__ == "__main__":
    download_and_extract()
