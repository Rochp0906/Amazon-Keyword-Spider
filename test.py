keyword = 'earbuds'
tarts = map(lambda k,p: f'https://www.amazon.com/s?k={k}&page={p}', [keyword for i in range(1, 51)],[page for page in range(1, 51)])
print(list(tarts))

# {'keyword': 'earbuds', 'url': 'https://www.amazon.com/dp/B07MZZZCXB', 'asin': 'B07MZZZCXB', 'titl
# e': 'TaoTronics Active Noise Cancelling Earbuds, in-Ear Headphones with 15 Hours Playtime Aware Mode, HiFi Stereo Bass, Wired Headphones with Built-in Microphone,
# Remote', 'brand': 'TaoTronics', 'picture': 'https://images-na.ssl-images-amazon.com/images/I/519T75A2qQL.jpg', 'stars': 3.7, 'reviews': 472, 'rank': ('10,066', 'Ce
# ll Phones & Accessories'), 'ranks': [('867', 'Earbud & In-Ear Headphones')], 'time': datetime.date(2019, 7, 31)}