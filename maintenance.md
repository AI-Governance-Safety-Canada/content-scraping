# Maintenance

This document describes some of the behind-the-scenes details, which may be
useful to maintainers.

## GitHub Workflow

There is a GitHub Actions workflow which can run the scraper and publish the
results to a predefined Google spreadsheet. It uses
[this classifier](https://github.com/AI-Governance-Safety-Canada/event-classifier)
to help determine the relevance of each event.

### Secrets

Rather than use a `.env` file, the workflow stores sensitive information using
GitHub secrets. The secrets are managed by going to Settings > Secrets and
variables > Actions.

Each secret corresponds to an environment variable in the `.env` file. See the
[`README`](/README.md) for instructions on how to create new values.

### Schedule

The workflow is configured to run automatically on a schedule.

### Running Manually

As an alterantive to the schedule, the workflow can be triggered manually.

1.  Navigate to the
    [Scrape and Publish workflow](https://github.com/AI-Governance-Safety-Canada/content-scraping/actions/workflows/scrape_and_publish.yml).
1.  Click the "Run workflow" button near the top right. If you don't see the
    button, you don't have the necessary permissions.
1.  Leave the branch set to `main`.
1.  If desired, override the URLs to scrape by entering them into the input box,
    separating them with spaces. If you leave this blank, the scraper will use
    the URLs defined in [`sources.py`](/scraper/events/sources.py).
1.  Click "Run workflow".
1.  Refresh the page to see the active workflow you just started. You can click
    on it to monitor its progress.
