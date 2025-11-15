# HPC Usage Guide for Mayo Clinic Crawlers

This guide explains how to run the Mayo Clinic crawlers on an HPC cluster using SLURM.

## Prerequisites

1. **Python Environment**: Ensure Python 3.7+ is available
2. **Dependencies**: Install required packages
   ```bash
   pip install beautifulsoup4 requests pyyaml
   ```
   Or create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install beautifulsoup4 requests pyyaml
   ```

3. **Modules**: Load required modules (adjust for your HPC system)
   ```bash
   module load python/3.9
   # or
   module load anaconda3
   ```

## SBATCH Scripts

Two sbatch scripts are provided:

### 1. Sequential Script (`run_crawlers.sbatch`)
Runs all crawlers sequentially in a single job. Best for smaller crawls or when you want all results in one job.

### 2. Array Script (`run_crawlers_array.sbatch`)
Runs crawlers in parallel using SLURM array jobs. Best for full crawls to save time.

## Usage Examples

### Basic Usage - Test Mode (Quick Test)
```bash
# Test all crawlers with 5 items each
sbatch --export=MODE=test run_crawlers.sbatch

# Test in parallel
sbatch --export=MODE=test run_crawlers_array.sbatch
```

### Sample Mode (50 items each)
```bash
# Sequential
sbatch --export=MODE=sample run_crawlers.sbatch

# Parallel
sbatch --export=MODE=sample run_crawlers_array.sbatch
```

### Full Crawl (All items)
```bash
# Sequential - runs one crawler after another
sbatch run_crawlers.sbatch

# Parallel - runs all three crawlers simultaneously
sbatch run_crawlers_array.sbatch
```

### Run Specific Crawler Only
```bash
# Only diseases crawler
sbatch --export=CRAWLER_TYPE=diseases run_crawlers.sbatch

# Only drugs/supplements crawler
sbatch --export=CRAWLER_TYPE=drugs run_crawlers.sbatch

# Only symptoms crawler
sbatch --export=CRAWLER_TYPE=symptoms run_crawlers.sbatch
```

### With Custom Delay
```bash
# Use 3 second delay between requests (be more polite)
sbatch --export=DELAY=3.0 run_crawlers.sbatch

# Use 1 second delay (faster, less polite)
sbatch --export=DELAY=1.0 run_crawlers.sbatch
```

### Array Job - Run Specific Crawlers
```bash
# Run only diseases (array task 0)
sbatch --array=0 run_crawlers_array.sbatch

# Run only drugs (array task 1)
sbatch --array=1 run_crawlers_array.sbatch

# Run only symptoms (array task 2)
sbatch --array=2 run_crawlers_array.sbatch

# Run diseases and symptoms only (tasks 0 and 2)
sbatch --array=0,2 run_crawlers_array.sbatch
```

### Combining Options
```bash
# Test mode with 3 second delay, only symptoms
sbatch --export=MODE=test,DELAY=3.0,CRAWLER_TYPE=symptoms run_crawlers.sbatch

# Sample mode with parallel execution and custom delay
sbatch --export=MODE=sample,DELAY=2.5 run_crawlers_array.sbatch
```

## Customizing for Your HPC System

### 1. Update SBATCH Directives
Edit the `#SBATCH` lines at the top of each script:

```bash
#SBATCH --partition=standard      # Change to your partition name
#SBATCH --mail-user=your.email@domain.edu  # Your email
#SBATCH --time=24:00:00          # Adjust time limit
#SBATCH --mem=8G                 # Adjust memory
```

### 2. Load Modules
Uncomment and modify the module loading section in the scripts:

```bash
# Example for common HPC setups:
module load python/3.9
# OR
module load anaconda3
# OR
module load python/3.11-anaconda
```

### 3. Activate Virtual Environment
If using a virtual environment, uncomment and update the path:

```bash
source /path/to/your/venv/bin/activate
# OR for conda:
conda activate mayo_crawler
```

## Monitoring Jobs

### Check job status
```bash
squeue -u $USER
```

### View output logs
```bash
# Sequential job
tail -f logs/crawler_<JOB_ID>.out

# Array job (replace JOBID and TASKID)
tail -f logs/crawler_array_<JOB_ID>_<TASK_ID>.out
```

### Cancel a job
```bash
scancel <JOB_ID>

# Cancel specific array task
scancel <JOB_ID>_<TASK_ID>
```

## Output Structure

Crawlers will create the following directories:
```
mayo_clinic_data/        # Diseases and conditions
  ├── markdown/
  ├── yaml/
  └── crawl_report.json

drug_supplement_data/    # Drugs and supplements
  ├── markdown/
  ├── yaml/
  └── crawl_report.json

symptom_data/            # Symptoms
  ├── markdown/
  ├── yaml/
  └── crawl_report.json
```

## Resource Recommendations

### For Test Mode (5 items each)
- Time: 1 hour
- Memory: 2GB
- CPUs: 1

### For Sample Mode (50 items each)
- Time: 4 hours
- Memory: 4GB
- CPUs: 1-2

### For Full Crawl (All items)
- Sequential: Time: 24-48 hours, Memory: 8GB
- Array (parallel): Time: 12-24 hours per crawler, Memory: 4GB per task

## Troubleshooting

### Permission denied
```bash
chmod +x run_crawlers.sbatch run_crawlers_array.sbatch
```

### Module not found
Check available Python modules:
```bash
module avail python
module avail anaconda
```

### Out of memory
Increase memory in SBATCH directive:
```bash
#SBATCH --mem=16G
```

### Time limit exceeded
Increase time limit:
```bash
#SBATCH --time=48:00:00
```

Or run in test/sample mode first to estimate time needed.

## Best Practices

1. **Start with test mode** to verify everything works
2. **Use appropriate delays** (2-3 seconds) to be respectful to Mayo Clinic servers
3. **Monitor initial runs** to ensure crawlers are working correctly
4. **Use array jobs** for full crawls to parallelize and save time
5. **Check logs** regularly for errors or issues
6. **Set email notifications** to know when jobs complete

## Environment Variables Reference

| Variable | Options | Default | Description |
|----------|---------|---------|-------------|
| MODE | test, sample, all | all | Crawling mode (5, 50, or all items) |
| DELAY | float (seconds) | 2.0 | Delay between requests |
| CRAWLER_TYPE | diseases, drugs, symptoms, all | all | Which crawler(s) to run |

## Example Workflow

```bash
# 1. First time setup
module load python/3.9
python -m venv venv
source venv/bin/activate
pip install beautifulsoup4 requests pyyaml

# 2. Test the setup
sbatch --export=MODE=test run_crawlers.sbatch

# 3. Check if it's working
squeue -u $USER
tail -f logs/crawler_*.out

# 4. Once confirmed, run full crawl in parallel
sbatch run_crawlers_array.sbatch

# 5. Monitor progress
watch -n 60 'squeue -u $USER'
ls -lh *_data/crawl_report.json
```
