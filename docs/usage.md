# Использование Simple VCS

## Базовые команды

- `svcs init` - инициализация репозитория
- `svcs add <file>` - добавление файла в индекс
- `svcs commit -m "message"` - создание коммита
- `svcs log` - просмотр истории
- `svcs status` - статус репозитория

## Пример workflow

```bash
svcs init
echo "Hello" > file.txt
svcs add file.txt
svcs commit -m "Add file"
svcs log
```
