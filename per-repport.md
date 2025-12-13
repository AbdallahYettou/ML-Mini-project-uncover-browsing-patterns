

## Purpose

The preprocessing converts the NASA HTTP server logs into session transactions suitable for association-rule mining (Apriori, ECLAT, FP-Growth) and other session-based analyses. Association-rule mining needs transactions (lists of items). Preprocessing turns noisy raw logs into meaningful transactions (sessions). (transaction = a list of items used by a mining algorithm; session = one user visit). ([VLDB][1])


---

## Project files involved

* `extract_logs.py` — extracts `GET` requests, groups requests by host, and writes raw sessions to `extracted_logs.csv`.


* `clean_extracted_data.py` — normalizes and filters paths, removes noise and consecutive duplicates, and writes session transactions to `cleaned_data.csv`.

* Input logs: `Data/Logs/access_log_Jul95` and `Data/Logs/access_log_Aug95`.




---

## Pipeline summary

### 1. Extraction (`extract_logs.py`)

* Parse lines that are `GET` requests and extract `host`, `path`, and `status`. (host = IP or hostname; status = HTTP response code). ([Apache HTTP Server][2])
* Skip lines that do not match the pattern and skip responses with `status >= 400` (error responses).
* Group requests by host and write a comma-separated sequence of paths for each host into `extracted_logs.csv`. (host-based sessionization)



---

### 2. Cleaning (`clean_extracted_data.py`)

#### Path Normalization
* Remove query strings and fragments (parts after `?` or `#`). (query string = text after `?` often used for parameters).
* Normalize multiple slashes (`//`) to a single slash (`/`).
* Remove trailing slashes (except root `/`).
* If the request target looks like a file (basename contains `.`), use the parent directory (directory-level normalization). (basename = last part of the path)

#### Noise Path Filtering
Remove known noise/static directories and patterns:
* **Static resources**: `/images`, `/icons`, `/css`, `/js`, `/fonts`, `/media`, `/static`, `/assets`
* **CGI paths**: `/cgi-bin`, `/htbin`, and any path containing `imagemap` (coordinate-based links)
* **Malformed paths**: Paths containing commas (usually coordinate data or parsing errors)
* **Numeric paths**: Paths that are just numbers (e.g., `283`, `224` - often errors)
* **Short paths**: Paths with fewer than 3 characters (not meaningful navigation)

#### Path Depth Limiting
* Limit paths to **3 levels** maximum to avoid overly specific patterns.
* Example: `/shuttle/missions/sts-69/images/photo.gif` → `/shuttle/missions/sts-69`
* This improves pattern generalization and reduces noise from deep directory structures.

#### Session Processing
* Remove consecutive duplicate paths in a session (to ignore page refreshes).
* **Limit session length** to **25 pages** maximum (very long sessions add noise and can skew results).
* Write sessions that contain at least **2 cleaned paths** to `cleaned_data.csv`.

#### Preprocessing Results
| Metric | Before Cleaning | After Cleaning |
|--------|-----------------|----------------|
| Total Sessions | 69,413 | 45,127 |
| Avg Paths/Session | 22.31 | 6.78 |
| Total Paths | 1,548,518 | 305,744 |

Preprocessing steps like these are common in web-usage mining. ([ResearchGate][3])



---

## Inputs (sample lines)

**`Data/Logs/access_log_Aug95`**

```txt
www-c3.proxy.aol.com - - [01/Aug/1995:00:00:59 -0400] "GET /htbin/cdt_main.pl HTTP/1.0" 200 3714
in24.inetnebr.com - - [01/Aug/1995:00:01:02 -0400] "GET /shuttle/missions/sts-68/news/sts-68-mcc-07.txt HTTP/1.0" 200 1437
...
```

**`Data/Logs/access_log_Jul95`**

```txt
199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245
unicomp6.unicomp.net - - [01/Jul/1995:00:00:06 -0400] "GET /shuttle/countdown/ HTTP/1.0" 200 3985
...
```

---

## Outputs (files)

* `Data/extractedAndcleanedData/extracted_logs.csv` — raw per-host path sequences (pre-cleaning).
* `Data/extractedAndcleanedData/cleaned_data.csv` — cleaned session transactions ready for mining.

**Example :**

```
[['/history/apollo', '/history'], ['/shuttle/countdown', '/facilities'], ['/shuttle/missions/sts-73'], ['/shuttle/countdown/video'], ['/shuttle/countdown', '/shuttle/missions/sts-71/images'], ['/shuttle/countdown'], ['/shuttle/missions/51-l', '/shuttle/technology/sts-newsref'], ['/facts'], ['/shuttle/missions/sts-71/images'], ['/shuttle/countdown', '/shuttle/missions/sts-71/images']]
```


