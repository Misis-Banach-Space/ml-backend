import pandas as pd

from serpapi import GoogleSearch


search = GoogleSearch({
    "q": "Ветиренарные услуги", 
    "location": "Russia",
    'num': "35",
    "api_key": "7b77cc657efa401ae63c9aca4f6d83d600797688812a6b0e062f29d36455dddd"
  })
result = search.get_dict()
result['search_metadata']
# with open('text.txt', 'w') as f:
    # f = f.write(result['search_metadata'])
ans = pd.DataFrame([result['organic_results'][i]['link'] for i in range(len(result['organic_results']))])
ans.to_csv('test2.csv', index=False)
print(ans)