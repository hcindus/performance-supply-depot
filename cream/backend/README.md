# CREAM Backend API

Express.js REST API for CREAM - Comprehensive Real Estate Agent Management

## Setup

```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your settings
npm start
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 3000 |
| NODE_ENV | Environment | development |
| JWT_SECRET | JWT signing secret | (change in production!) |
| FRONTEND_URL | CORS allowed origin | * |
| MONGODB_URI | MongoDB connection string | (optional) |

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update profile
- `POST /api/auth/logout` - Logout

### Leads
- `GET /api/leads` - List leads
- `POST /api/leads` - Create lead
- `GET /api/leads/:id` - Get lead
- `PUT /api/leads/:id` - Update lead
- `DELETE /api/leads/:id` - Delete lead
- `POST /api/leads/bulk` - Bulk import
- `GET /api/leads/stats/summary` - Lead statistics

### Appointments
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `GET /api/appointments/upcoming` - Upcoming (7 days)
- `POST /api/appointments/:id/result` - Record result

### Invoices
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Create invoice
- `PUT /api/invoices/:id` - Update invoice
- `POST /api/invoices/:id/pay` - Mark paid

### Properties
- `GET /api/properties` - List properties
- `POST /api/properties` - Create listing
- `PUT /api/properties/:id` - Update
- `DELETE /api/properties/:id` - Delete

## Authentication

All protected routes require Bearer token:
```
Authorization: Bearer <token>
```

## Running

```bash
npm start        # Production
npm run dev     # Development with nodemon
```

## Status

🔄 Backend skeleton complete
⏳ Need MongoDB integration for production
⏳ Add email/SMS notifications
⏳ Add AI Lead Scoring endpoint
