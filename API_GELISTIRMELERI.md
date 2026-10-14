# API Geliştirmeleri

Bu not, API ile ilgili bu konuşmada ele alınan KAI-Flow geliştirmelerini ve `codex/api-integrations` dalındaki kapsamı özetler. Dal, güncel `origin/dev` tabanından oluşturulmuştur.

## Entegrasyon düğümleri

Gmail ve Google Sheets düğümleri güncel `dev` dalında bulunur; bu dalda mevcut uygulamaları kullanılır:

- **Gmail** (`backend/app/nodes/processing/gmail_node.py`): workflow içinden e-posta arama, okuma, gönderme ve ileti yönetimi işlemleri.
- **Google Sheets** (`backend/app/nodes/integrations/google_sheets_node.py`): kimlik bilgileriyle e-tablo okuma ve yazma işlemleri.
- **SQLite** (`backend/app/nodes/databases/sqlite_node.py`, `backend/app/nodes/tools/sqlite_tool.py`): workflow ve agent araçlarından SQLite işlemleri. Güvenli sorgu yürütme, yapılandırılmış tablo işlemleri ve erişim izinleri desteklenir.

## SQLite şema keşif API’si

Bu dal, SQLite düğümü yapılandırmasını kolaylaştıran iki kimlik doğrulamalı `GET` endpoint’i ekler:

| Endpoint | Parametreler | Yanıt |
| --- | --- | --- |
| `/api/v1/sqlite/tables` | `credential_id` (zorunlu), `search` (isteğe bağlı) | Erişilebilir tablo ve görünümlerin adı/türü; en fazla 200 kayıt |
| `/api/v1/sqlite/columns` | `credential_id`, `table` (zorunlu) | Seçilen tablonun kolon adı, SQLite tipi, null olabilirliği, varsayılan değeri ve birincil anahtar bilgisi |

API, kimlik bilgisini oturum açmış kullanıcı adına çözer; kimlik bilgisinin `sqlite` türünde olduğunu doğrular ve veritabanı dosya yolunu yanıt olarak döndürmez. SQLite metadata sorguları async event loop’u bloklamamaları için iş parçacığı havuzunda çalıştırılır. Tablolar aranırken parametreli sorgu, kolonlar okunurken doğrulanmış/escape edilmiş tanımlayıcı kullanılır.

İstemci tarafındaki `client/app/services/sqliteService.ts`, bu endpoint’ler için tipli tablo ve kolon çağrıları sağlar. API yolları `client/app/lib/config.ts` içindeki `API_ENDPOINTS.SQLITE` altında tanımlıdır.

## Dal kapsamı

Gmail, Google Sheets ve temel SQLite düğüm uygulamaları `dev` tabanında zaten bulunduğundan, eski çalışma klasöründeki yinelenen kopyaları bu dala taşımadım. Bu dalın yeni backend API kapsamı SQLite tablo/kolon keşfi ve router kaydıdır; istemci tarafında da buna karşılık gelen endpoint sabitleri ve servis istemcisi yer alır.
