# Deployment

Fill in during Block 8. Target stack:

- Backend: Docker image on a VPS, behind Nginx + Let's Encrypt
- DB: managed Postgres (RDS / DigitalOcean) with daily backups
- Flutter web (admin): static hosting (S3 + CloudFront / Netlify)
- Flutter mobile: Play Store internal track
