# Dashboard

A modern web interface for monitoring and managing RegulaAI scraping tasks.

## Features

- Real-time monitoring of scraping tasks
- Rule configuration and management
- Data visualization
- User authentication and authorization
- Responsive design with Tailwind CSS

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Development

- Uses React 18+ with TypeScript
- Styled with Tailwind CSS
- State management with React Query
- Component testing with Jest and React Testing Library

## Project Structure

```
dashboard/
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/        # Page components
│   ├── hooks/        # Custom React hooks
│   ├── services/     # API services
│   └── utils/        # Utility functions
├── public/           # Static assets
└── tests/           # Test files
``` 