# Frontend (Flutter)

Three Flutter projects share a common package (`packages/sewa_core`) for API client,
models, and theming.

```
frontend/
├── packages/
│   └── sewa_core/         Shared Dart package (API client, models, theme)
├── customer_app/          Mobile app — Block 4
├── shopkeeper_app/        Mobile app — Block 5
└── admin_dashboard/       Flutter Web — Block 6
```

## Bootstrapping each app

These directories contain placeholder `pubspec.yaml` + `lib/main.dart` stubs.
Before serious work in a given block, run:

```bash
cd frontend/customer_app
flutter create . --project-name customer_app --platforms=android,ios
flutter pub get
flutter run
```

`flutter create .` will fill in Android/iOS/web scaffolding around the existing
`lib/` and `pubspec.yaml`.
