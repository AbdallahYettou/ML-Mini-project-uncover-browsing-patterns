

# **Article — Preprocessing NASA HTTP Web Server Logs for Web Usage Mining**

## **1. Introduction**

Web server log files, such as the NASA HTTP logs from July and August 1995, are rich sources of behavioral information that can be used to uncover browsing patterns, session flows, and frequently co-accessed pages. However, the raw log files are *not* directly usable for analysis. They contain unstructured text, inconsistent fields, missing values, and a format that requires parsing before any meaningful machine learning or statistics can be applied.

To address these challenges, a dedicated **preprocessing pipeline** is required. This phase converts raw logs into clean, structured, and enriched data suitable for downstream tasks such as sessionization, association rule mining (Apriori), and clustering.

---

## **2. Structure of the NASA Log Data**

Each entry in the NASA log files follows a standard HTTP Common Log Format:

```
host ident authuser [date:time zone] "request" status bytes
```

For example:

```
199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245
```

From this line, we can extract:

* **Host:** `199.72.81.55`
* **Timestamp:** `01/Jul/1995 00:00:01 -0400`
* **HTTP Method:** `GET`
* **Resource Path:** `/history/apollo/`
* **Protocol:** `HTTP/1.0`
* **Status Code:** `200`
* **Bytes Transferred:** `6245`

While the structure appears regular, real logs contain:

* Missing values
* Corrupted or malformed lines
* “-” for missing bytes
* Inconsistent path formats
* Duplicate slashes
* Multiple time zones
* Different casing or file extensions

These issues justify the need for preprocessing.

---

## **3. Objectives of Preprocessing**

The preprocessing step has several goals:

1. **Parse** raw log text into structured fields.
2. **Clean** missing, inconsistent, or corrupted entries.
3. **Normalize** time and resource formats.
4. **Derive new features** needed for analytics.
5. **Output a structured dataset**, such as a CSV, suitable for:

   * Apriori algorithms
   * User session identification
   * Clustering
   * Visualization

Preprocessing serves as the foundation of the entire analysis pipeline.

---

## **4. Preprocessing Steps**

### **4.1 Log Parsing**

The first step is extracting the fields from each log entry.
This involves using regular expressions to split each line into:

* host
* timestamp
* method, resource, protocol
* status
* bytes

Lines that do not match the expected structure are discarded.

---

### **4.2 Data Cleaning**

This step ensures the resulting dataset is consistent and error-free.

#### **A. Removing malformed entries**

Some lines do not contain a valid request, or have incomplete fields. These are filtered out.

#### **B. Handling missing bytes**

In some logs, byte values appear as `"-"`.
These are replaced with `0` and cast to integers.

#### **C. Normalizing timestamps**

Timestamps are:

* parsed into Python datetime objects
* timezone-corrected
* optionally converted to UTC

This allows grouping by hour, day, and session.

#### **D. Cleaning resource paths**

Operations include:

* converting paths to lowercase
* removing duplicate slashes
* stripping query parameters
* reducing `/` to root when empty

This produces clean, consistent URLs.

---

### **4.3 Feature Engineering**

To support downstream analytics, extra fields are generated:

* **day**, **hour**, **month**
* **resource type** (html, gif, txt…)
* **is_error** (status ≥ 400)
* **response_size_category**
* **weekday** extracted from timestamp

These enriched features improve clustering and usage pattern detection.

---

### **4.4 Merging Multiple Log Files**

The July and August 1995 datasets are combined into a single uniform dataset, making it possible to analyze multi-month traffic patterns.

---

### **4.5 Exporting a Clean Dataset**

Finally, the cleaned and fully structured dataset is exported as:

```
clean_nasa_logs.csv
```

This file becomes the input for:

* the **Apriori** frequent itemset miner
* **user session reconstruction**
* **clustering algorithms**
* **visualization tools (e.g., Tableau)**

---

## **5. Importance of Preprocessing in Web Usage Mining**

Preprocessing is often the most time-consuming step, but also the most crucial.
Inaccurate or incomplete log data leads to unreliable mining results.

A well-designed preprocessing pipeline ensures:

* consistent resource paths
* accurate session reconstruction
* realistic page co-occurrence matrices
* meaningful similarity measures
* reduced noise and bias

In web usage mining, preprocessing can influence **over 70% of the final model’s quality**.

---

## **6. Conclusion**

The NASA web server logs provide a rich dataset for studying user behavior, but raw logs are not directly usable. Preprocessing is essential to transform messy text files into reliable, consistent, analytic-ready data. Through parsing, cleaning, normalization, feature engineering, and merging, we build a solid foundation for advanced tasks such as session analysis, frequent browsing pattern discovery, and clustering of web content.
A robust preprocessing workflow ensures that the insights drawn from the dataset truly reflect user behavior and not noise or inconsistencies in the raw logs.

---

**note:**
It's often helpful to visualize the distribution of resources after preprocessing. Observing which paths dominate the traffic gives early insight into user interests and potential anomalies.

---

# **Article — Session-Based Preprocessing for Association Rule Mining**

## **1. Overview**

In addition to the general log preprocessing described above, a specialized **session-based preprocessing script** (`perproccing.py`) was developed to prepare data specifically for association rule mining algorithms such as **Apriori** and **FP-Growth**.

The goal is to transform raw NASA HTTP logs into **user sessions** — sequences of pages visited by each unique host — that can be used to discover frequent browsing patterns and page associations.

---

## **2. Implementation Details**

### **2.1 Path Cleaning (`clean_path` function)**

Each requested URL path undergoes the following transformations:

| Operation | Description |
|-----------|-------------|
| **Query string removal** | Strips everything after `?` or `#` |
| **Slash normalization** | Replaces multiple consecutive slashes with a single slash |
| **Trailing slash removal** | Removes trailing `/` from paths |
| **File extension handling** | If the path ends with a file (e.g., `.html`, `.gif`), only the parent directory is kept |

**Example:**
```
Input:  /shuttle/missions/sts-71/images/KSC-95EC-0912.jpg?v=2
Output: /shuttle/missions/sts-71/images
```

---

### **2.2 Path Validation (`is_valid_path` function)**

Not all paths are meaningful for session analysis. In web usage mining, we focus on **intentional user navigation** — pages users actively choose to visit. Auxiliary resources like images and icons are automatically loaded when a page renders, creating "false" associations that add noise without insight.

The following paths are filtered out:

| Filtered Path Type | Reason |
|--------------------|--------|
| `/` (root) | Too generic, provides no specific navigation information |
| `/cgi-bin/*` | Dynamic CGI scripts, not actual content pages |
| `/htbin/*` | Server-side scripts, often internal/automated requests |
| `/icons/*` | Static icon files loaded automatically by browsers |
| `/images` (standalone) | Generic images directory, auto-loaded resources |

**Why filter these paths?**

1. **Reduce noise in association rules**: If `/images` appears in almost every session (because every page loads images), it would dominate the frequent itemsets without providing actionable insights.

2. **Focus on meaningful navigation**: We want to discover patterns like "users who visit `/history/apollo` also visit `/shuttle/missions`" — not that "every user visits `/images`".

3. **Improve algorithm performance**: Fewer items means faster computation and more interpretable results.

4. **Better quality rules**: Filtering noise paths leads to association rules with higher lift and practical value for recommendations.

---

### **2.3 Duplicate Removal (`remove_consecutive_duplicates` function)**

Users often refresh pages or make repeated requests to the same resource. Consecutive duplicate paths within a session are removed to reduce noise.

**Example:**
```
Before: /history/apollo, /history/apollo, /history/apollo/apollo-13, /history/apollo/apollo-13
After:  /history/apollo, /history/apollo/apollo-13
```

---

### **2.4 Session Construction**

Sessions are constructed by grouping all requests by their **source host** (IP address or domain). This provides a simple but effective sessionization strategy based on the assumption that each unique host represents a unique user.

**Minimum session length:** Only sessions with **2 or more paths** are included in the output. Single-page visits provide no association information.

---

## **3. Processing Pipeline**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Raw Log Files                                │
│         access_log_Jul95 + access_log_Aug95                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Regex Parsing                                │
│         Extract: host, path, status code                        │
│         Filter: Only GET requests                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Error Filtering                              │
│         Skip: HTTP status >= 400 (errors)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Path Cleaning                                │
│         Remove: query strings, file extensions                  │
│         Normalize: slashes                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Path Validation                              │
│         Filter out: cgi-bin, htbin, icons, root                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Session Grouping                             │
│         Group paths by host                                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output: perproccing.csv                      │
│         One session per line (comma-separated paths)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## **4. Results**

After processing both log files, the following statistics were obtained:

| Metric | Value |
|--------|-------|
| **Total sessions** | 89,721 |
| **Total paths** | 1,022,841 |
| **Average paths per session** | 11.40 |

**Sample output (perproccing.csv):**
```csv
/shuttle/resources/orbiters,/history/apollo/apollo-17,/shuttle/missions/sts-71/images
/history/apollo,/history/apollo/apollo-13,/shuttle/missions/sts-70
/shuttle/countdown,/facilities,/shuttle/technology/sts-newsref
```

Each line represents one user session with comma-separated page paths, ready for use with association rule mining algorithms.

---

## **5. Usage with Association Rule Mining**

The output file `perproccing.csv` is directly compatible with:

- **Apriori algorithm** — to find frequent itemsets of co-visited pages
- **FP-Growth algorithm** — for efficient frequent pattern mining
- **Sequential pattern mining** — to discover common navigation sequences

These algorithms can reveal insights such as:
- Pages that are frequently visited together
- Common navigation paths through the website
- Potential candidates for link recommendations

---

## **6. Conclusion**

The session-based preprocessing script transforms raw NASA HTTP logs into clean, structured session data optimized for association rule mining. By filtering noise, removing duplicates, and grouping requests by host, the output provides a high-quality dataset for discovering meaningful browsing patterns and page associations.
