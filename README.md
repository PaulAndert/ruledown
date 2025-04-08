# Ruledown

Downloads imges from your Rule34 Favorites Page. Automatically skips images already downloaded.

# Requirement

```
pip install requests
```

# Usage

Provide input parameter either via the commandline or if not the script asks for them.

### Commandline

```
python3 main.py -uid=<id> -path=<path> -page=<page_number>
```

__\<uid\>__ is found on your 'My Profile' Page in the URL  
https://rule34.xxx/index.php?page=account&s=profile&id=\<id\>

__\<path\>__ is the absolute path to the folder where the imgages are to be saved  
  
__\<page\>__ is either the page number that should be downloaded or the keyword 'all' to download all pages