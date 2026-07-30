# MySQL Test Workflows

Bu klasörde altı ayrıntılı özellik testi ve güncel sürümü hızlıca doğrulamak için iki açıklamalı workflow bulunur.

## Çalıştırmadan önce

1. Yerel veritabanını `docker compose up -d mysql` ile başlatın.
2. MySQL credential oluşturun. Docker örneği için host `localhost`, port `3306` ve database `kai_demo` değerlerini kullanın.
3. Workflow içindeki her MySQL veya MySQL Tool node'unda bu credential'ı seçin.
4. Agent workflow'u için OpenAI Chat node'unda ayrıca bir LLM credential seçin.

Credential UUID'leri ve secret değerleri güvenlik nedeniyle JSON şablonlarına gömülmemiştir.

## Güncel sürüm için önerilen iki workflow

| Şablon | Ne test eder? |
|---|---|
| `mysql-current-crud-test.json` | Normal MySQL node'unda tablo oluşturma, insert, upsert, update, filtreli select, JSON uyumlu çıktı ve test kaydını temizleme |
| `mysql-current-agent-tool-test.json` | Ayrı MySQL Tool node'u, `tool -> Agent.tools` bağlantısı, read-only profil, tablo allowlist'i, sonuç limiti ve yazma isteğinin reddedilmesi |

Her iki workflow da canvas üzerinde kurulum adımlarını ve beklenen sonuçları açıklayan en az üç Sticky Note içerir.

## Ayrıntılı özellik testleri

| Şablon | Kapsam |
|---|---|
| Test 01 | Setup, auto-map, manuel mapping, insert, upsert, update, filtreli select, empty-to-NULL, priority, conflict skip, batching, çıktı dönüşümleri ve cleanup |
| Test 02 | `$1`, `$2`, `$1:name`, parametre setleri, AND/OR filtreleri, DISTINCT, sorting, limit, Return All, BIGINT ve DECIMAL modları |
| Test 03 | Filtreli DELETE, TRUNCATE, DROP, çoklu sonuç ve cleanup |
| Test 04 | Bağımsız commit, duplicate-key hatası, Continue on Fail, ayrıntılı hata ve INSERT IGNORE |
| Test 05 | Ayrı MySQL Tool, `tool -> Agent.tools`, özel tool adı, read-only SELECT ve yazma engeli |
| Test 06 | Yalnız disposable `mysql_agent_full_test` tablosunda full-admin Agent işlemleri |

## Agent workflow'unda denenebilecek mesajlar

- `customers tablosundaki ilk 5 müşterinin isim ve e-posta bilgilerini getir.`
- `orders tablosundaki sipariş sayılarını durumlara göre grupla.`
- `customers tablosundaki tüm kayıtları sil.` — read-only profil tarafından reddedilmelidir.

## Credential seviyesindeki özellikler

SSL sertifikaları ve SSH tunnel workflow node alanı değil, credential bağlantı özellikleridir. Sertifika, private key, host veya parola gibi ortama özel secret değerler tekrar kullanılabilir şablonlara eklenmemelidir. Bunları ayrı credential'larla `Test Connection` üzerinden doğruladıktan sonra aynı credential'ı yukarıdaki workflow'larda kullanın.

`Connections Limit` formda gösterilir ancak mevcut PyMySQL implementasyonu bağlantı havuzu oluşturmadığı için şu anda runtime pool limiti uygulamaz.
