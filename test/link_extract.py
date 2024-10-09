def extract_link(file_path):
  import pandas as pd
  import re

  # Load your CSV file
  df = pd.read_csv(file_path)

  # Function to extract usernames and links from the 'CONTENT' column
  def extract_usernames_links(content):
      # Regex pattern to capture any URL in the content
      pattern = r'(https?://[^\s<>"\']+)'
      matches = re.findall(pattern, content)
      return matches

  # Apply the function to the 'CONTENT' column
  df['USERNAMES_AND_LINKS'] = df['CONTENT'].apply(lambda x: extract_usernames_links(str(x)))

  # Filter out empty lists
  links = [link for link in df['USERNAMES_AND_LINKS'] if link]
  flat_list = [link for sublist in links for link in sublist]

  # Print the final list of links
  return flat_list

print('LInks : ',extract_link(r'D:\ihub\social\output\user_data\madhan.king51@gmail.com\messages.csv'))