# Continuous Integration and Deployment

This document describes the CI/CD workflow for the Windows Developer Utilities Toolkit.

## GitHub Actions Workflow

Our project uses GitHub Actions to automate testing, building, and deployment processes. The workflow is defined in `.github/workflows/main.yml`.

### Workflow Triggers

The workflow is triggered by:
- Pushing commits to the `main` branch
- Creating or updating a pull request targeting the `main` branch

### Jobs

#### 1. Test

This job runs on every commit and pull request:
- Sets up a Windows environment with Python
- Installs dependencies
- Runs linting checks (black, flake8, isort, mypy)
- Runs all tests with coverage reporting

#### 2. Build

This job runs after tests pass:
- Builds the executable using PyInstaller
- Creates a versioned executable file
- For stable builds (main branch): Uses format `YYYY.MM.DD.HHMM`
- For unstable builds (PRs): Uses format `YYYY.MM.DD.HHMM-unstable`
- Uploads the build as a GitHub artifact

#### 3. PR Comment (Pull Requests Only)

This job runs only on pull requests:
- Gets the URL for the unstable build artifact
- Comments on the PR with a download link
- Indicates the build status

## Branch Protection

The repository is configured with branch protection rules (see `.github/branch-protection.yml`):

- The `main` branch is protected:
  - Pull requests are required for changes to main
  - At least one review approval is required
  - Status checks must pass before merging
  - Required status checks: "Test" and "Build"
  - Branches must be up to date before merging
  - All conversations must be resolved before merging

## Development Workflow

1. Create a new branch for your feature or fix
2. Make your changes with appropriate tests
3. Create a pull request to the `main` branch
4. The CI workflow will automatically:
   - Run tests and linting
   - Build an unstable version of the executable
   - Comment on the PR with a download link
5. Address any feedback or failed tests
6. Once tests pass and you have required approvals, you can merge
7. After merging to main, a stable build will be created

## Downloading Builds

- **Stable builds**: Available as artifacts from workflow runs on the main branch
- **Unstable builds**: Available as artifacts from pull request workflow runs
  
> **Note**: You need to be logged in to GitHub to download workflow artifacts.

## Troubleshooting CI/CD Issues

If you encounter issues with the CI/CD pipeline:

1. Check the GitHub Actions logs for error messages
2. Ensure all dependencies are properly declared in `pyproject.toml`
3. Verify your code passes linting and tests locally before pushing
4. For build issues, check PyInstaller compatibility with your code