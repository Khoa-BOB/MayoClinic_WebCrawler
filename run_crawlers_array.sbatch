#!/bin/bash
#SBATCH --job-name=mayo_crawlers_array
#SBATCH --output=logs/crawler_array_%A_%a.out
#SBATCH --error=logs/crawler_array_%A_%a.err
#SBATCH --time=10:00:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1
#SBATCH --partition=bigTiger
#SBATCH --array=0-2


# Mayo Clinic Crawler Array Job Script
# This script runs crawlers in parallel using SLURM array jobs
# Each array task handles one crawler type
#
# Usage:
#   sbatch run_crawlers_array.sbatch                    # Run all crawlers in parallel
#   sbatch --export=MODE=test run_crawlers_array.sbatch # Test mode
#   sbatch --array=0 run_crawlers_array.sbatch          # Run only diseases
#   sbatch --array=1 run_crawlers_array.sbatch          # Run only drugs
#   sbatch --array=2 run_crawlers_array.sbatch          # Run only symptoms

set -e
set -u
set -o pipefail

# Configuration
MODE="${MODE:-all}"
DELAY="${DELAY:-2.0}"

# Create logs directory
mkdir -p logs

# Define crawler configurations
declare -a CRAWLERS=("diseases" "drugs" "symptoms")
CRAWLER_TYPE="${CRAWLERS[$SLURM_ARRAY_TASK_ID]}"

echo "================================="
echo "Mayo Clinic Crawler Array Job"
echo "================================="
echo "Job ID: ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}"
echo "Node: ${SLURM_NODELIST}"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Crawler Type: ${CRAWLER_TYPE}"
echo "Mode: ${MODE}"
echo "Delay: ${DELAY}s"
echo "Start time: $(date)"
echo "================================="
echo

# Load modules (adjust for your HPC)
# module load python/3.9
# source /path/to/venv/bin/activate

# Run the appropriate crawler
case ${CRAWLER_TYPE} in
    diseases)
        if [ "${MODE}" = "test" ]; then
            python run_crawler.py --type diseases --mode test --delay ${DELAY}
        elif [ "${MODE}" = "sample" ]; then
            python run_crawler.py --type diseases --mode sample --delay ${DELAY}
        else
            python run_crawler.py --type diseases --mode all --delay ${DELAY}
        fi
        ;;
    drugs)
        if [ "${MODE}" = "test" ]; then
            python run_crawler.py --type drugs --mode test --delay ${DELAY}
        elif [ "${MODE}" = "sample" ]; then
            python run_crawler.py --type drugs --mode sample --delay ${DELAY}
        else
            python run_crawler.py --type drugs --mode all --delay ${DELAY}
        fi
        ;;
    symptoms)
        if [ "${MODE}" = "test" ]; then
            python run_symptom_crawler.py --limit 5 --delay ${DELAY}
        elif [ "${MODE}" = "sample" ]; then
            python run_symptom_crawler.py --limit 50 --delay ${DELAY}
        else
            python run_symptom_crawler.py --delay ${DELAY}
        fi
        ;;
esac

echo "================================="
echo "Crawler completed: ${CRAWLER_TYPE}"
echo "End time: $(date)"
echo "================================="
