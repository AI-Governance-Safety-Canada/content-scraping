# AIGS Content Scraping

## Instructions

### Setting Up

These steps only need to be done once.

#### `.env` File

This project uses parameters which should be kept private, such as API keys. To
keep them secret they are loaded as environment variables from a `.env` file.

To create your own `.env` file, first copy the example:

```bash
cp .env.example .env
```

The instructions in the following sections will walk you through configuring
your `.env` file.

#### Python Dependencies

Optionally create a virtual environment and activate it using
[these instructions](https://docs.python.org/3/tutorial/venv.html).

Install the Python dependencies by running

```bash
pip install -r requirements.txt
```

#### OpenAI API

This project uses [OpenAI's API](https://platform.openai.com/docs/overview) for
AI-powered web scraping.

1.  Create an OpenAI account and
    [API key](https://platform.openai.com/api-keys).
1.  Save the API key to the `.env` file you created above next to
    `OPENAI_API_KEY`.

Note that OpenAI imposes
[rate limits](https://platform.openai.com/docs/guides/rate-limits/usage-tiers)
on newly-created accounts.

#### Google Sheets

These steps are required if you want to publish the results to a Google
spreadsheet. They can safely be done at a later time if you'd prefer to only
store the results locally for now.

1.  Go to https://console.cloud.google.com/
1.  Select the project you wish to use or create a new one.
1.  Go to https://console.cloud.google.com/iam-admin/serviceaccounts
1.  Click "Create Service Account" near the top of the page
1.  Enter an ID and optionally a name and description.
1.  Click "Done" near the bottom. We can skip the optional steps.
1.  Under "Actions", click the three dots and select "Manage keys".
1.  Click "Add Key" and then "Create new key". Pick JSON for the key type.
1.  Your browser will download a JSON file containing the key. Open the file
    and copy the entire contents into your `.env` file under
    `GOOGLE_SERVICE_ACCOUNT_KEY`. Be sure to keep the single quotes and curly
    braces in place.
1.  Return to the
    [Service Accounts overview page](https://console.cloud.google.com/iam-admin/serviceaccounts).
1.  Copy the email address for the Service Account. It should have the form
    `service-account-id@project-123456.iam.gserviceaccount.com`.
1.  Open the spreadsheet where you'd like results to be published.
1.  Click the "Share" button in the top left.
1.  Share the sheet with the service account by pasting in its email address.
    _Be sure to set make it an Editor_.
1.  Copy the ID for the spreadsheet from its URL. The ID is a long string of
    letters and numbers.
    ```
    https://docs.google.com/spreadsheets/d/vIsx_YJu2tDVscuvLIe73-HGIZ_HDqf-k7DkTzrOEErr/edit?gid=0#gid=0
    #                                      ^------- this is the spreadsheet ID -------^
    ```
1.  Paste the ID into your `.env` file next to `GOOGLE_SPREADSHEET_ID`.
1.  Copy the name of the sheet (tab) where you want the results published. By
    default, it will have the name `Sheet1`.
1.  Paste the sheet name into your `.env` file next to `GOOGLE_SHEET_NAME`.

### Running

#### Scraping

Run `main.py`. The only required argument is the file where you'd like to save
the results.

```bash
python -m scraper output.csv
```

For more information, run

```bash
python -m scraper --help
```

#### Publishing

This project can publish the scrape results to a Google spreadsheet to make them
easy to share. Before proceeding, make sure you've followed the
[setup instructions above](#google-sheets).

Like the main module, there's one required argument: the CSV file containing the
results.

```bash
python -m scraper.common.exporters.google_sheets output.csv
```

For more information, run

```bash
python -m scraper.common.exporters.google_sheets --help
```

The script will append new rows to the bottom of the sheet. It checks the rows
already in the sheet to avoid duplicates.

### Maintenance

See [here](/maintenance.md) for maintenance information about this repository,
including the GitHub Actions workflow which can automatically run the steps
above.
