# Environment Setup

This project requires environment configuration files for TN5250 connection settings.

## Initial Setup

1. Copy the template files to create your local environment files:
   ```bash
   cp .env.template .env
   cp .env.sh.template .env.sh
   ```

2. Edit `.env` and `.env.sh` with your actual IBM i connection details:
   - `TN5250_HOST`: Your IBM i hostname
   - `TN5250_USER`: Your username
   - `TN5250_PASS`: Your password
   - `TN5250_DEVNAME`: Device name (optional)
   - `TN5250_MAP`: Code page mapping (default: 285)
   - `TN5250_SSL`: SSL connection flag (0 or 1)

## Important Notes

- The `.env` and `.env.sh` files are excluded from version control via `.gitignore`
- Never commit your actual credentials to the repository
- Always use the template files as a reference for required variables
