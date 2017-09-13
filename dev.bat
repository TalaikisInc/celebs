cd api_server
go run main.go
cd ../frontend
npm run dev
cd ../
python manage.py runserver 0.0.0.0:8001