✅ `README.md` sənədinə 139 və 140 nömrəli serverlərdə etdiyimiz bütün addımları, GitLab Runner konfiqurasiyasını, SSH açarların əlavə olunmasını və Flask tətbiqinin uğurla yerləşdirilməsini əhatə edən tam plan əlavə olundu.

İstəyirsənsə indi PDF faylına çevirim və ya başqa bir layihə sənədi də əlavə edə bilərik. Nə düşünürsən?

## Flask CI/CD Deployment with GitLab Runner

Bu sənəd 192.168.11.140 və 192.168.11.139 IP-ləri ilə iki server arasında Flask tətbiqinin Docker konteynerində CI/CD ilə qurulmasını və yerləşdirilməsini izah edir.

---

### 🖥️ Server 1 – GitLab (192.168.11.140)

**Quraşdırılmış və edilənlər:**
- GitLab serveri quruldu
- `flask-ci-demo` adlı GitLab reposu yaradıldı
- `.gitlab-ci.yml` faylı əlavə edildi
- `gitlab-runner` yükləndi və qeydiyyatdan keçirildi:
  ```bash
  sudo gitlab-runner register
  ```
- `python:3.11` image istifadə edilərək `docker` executor seçildi
- Runner aşağıdakı parametrlərlə qeyd edildi:
  - Description: `python-runner`
  - Tags: `docker`
- Runner aktivləşdirildi və konfiqurasiya faylı `/etc/gitlab-runner/config.toml` redaktə edildi:
  ```toml
  [[runners]]
    name = "python-runner"
    url = "http://192.168.11.140/"
    token = "<token>"
    executor = "docker"
    [runners.docker]
      image = "python:3.11"
      privileged = true
      volumes = ["/cache"]
  ```
- SSH açarı yaradıldı və GitLab dəyişənlərinə (`CI/CD -> Variables`) `SSH_PRIVATE_KEY` olaraq əlavə olundu


---

### 🖥️ Server 2 – Deploy Server (192.168.11.139)

**Quraşdırılmış və edilənlər:**
- `docker` və `docker-compose` quraşdırıldı
- `deployuser` adlı istifadəçi yaradıldı
- GitLab Runner SSH ilə bu serverə `scp` və `ssh` ilə bağlana bilir
- Port `5000` açıldı
- Layihə faylları `/home/deployuser/` altına göndərilir və orada konteyner işə salınır


---

### 📄 Layihə Faylları

**`.gitlab-ci.yml`:**
GitLab pipeline iki mərhələdən ibarətdir:
- `build`: Docker image qurur, gzip formatında saxlayır və digər serverə göndərir
- `deploy`: digər serverdə image yüklənir və konteyner işə salınır

**`Dockerfile`:**
```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

**`requirements.txt`:**
```
flask
```

**`app.py`:**
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Flask CI/CD İşləyir!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```


---

### ✅ Nəticə

- GitLab Runner düzgün qeydiyyatdan keçdi ✅
- Flask tətbiqi Docker ilə build olundu ✅
- Digər serverə `scp` ilə transfer edildi ✅
- `docker run` ilə Flask tətbiqi avtomatik start verdi ✅

**Deployment URL:**
```
http://192.168.11.139:5000
```

