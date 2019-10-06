## Тестовое задание для разработчиков

### 1. Управление проектом

#### 1.1 Сборка проекта

```
docker-compose build
```

#### 1.2 Запуск проекта
В интереактивном режиме
```
docker-compose up
```
В фоновом режиме
```
docker-compose up -d
```

#### 1.3 Остановка проекта
```
docker-compose down
```

### 2 Дополнение

Адрес веб-интерфейса  http://127.0.0.1:8080

настройки:
- Для работы сервиса test-streamer можно указать параметр STREAM_VIDEO. При значении True будет производить стрим файла в mjpeg-server.
- Можно укзаать свой файл, которы будет стримиться, в docker-compose.ymlв сервисе test-streamer

```
- FILEPATH=/home/bat/Video/small.mp4 #your file
```
