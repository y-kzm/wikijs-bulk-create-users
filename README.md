# Setup
```
$ cp .env.example .env
$ sed -i '' 's/^API_KEY=.*/API_KEY=your-api-key-here/' .env
$ sed -i '' 's/^WIKI_API_URL=.*/WIKI_API_URL=your-wikijs-api-endpoint-here/' .env
$ chmod +x setup.sh
$ ./setup.sh
```

# Show all users and groups
```
$ python3 get_users.py
```

# Bulk Create Users
```
$ python3 create_users.py 
Wiki.js ユーザー一括作成スクリプト
CSV ファイルのパスを入力: users.csv
```
> Note: `end_welcome_email`は常にnoで実行すること

# Reference
- [GraphQL API](https://docs.requarks.io/dev/api)