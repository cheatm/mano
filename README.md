# mano

用于定期读取mongodb中存储的数据服务对应的索引表并通过发送邮件监控每日数据更新情况。

## 使用docker-compose部署

模板文件 docker-compose-template.yml：
```bash
version: '3'
services:
  mano:
    container_name: mano
    build: .
    image: mano
    volumes:
      # 配置文件目录
      - "./conf:/conf"
      # 日志输出目录
      - ".:/logs"
    environment:
      # mongodb地址
      MONGODB_URI: "localhost:27017"
      # db名
      DB_NAME: ""
      # 邮箱服务器地址，默认腾讯企业邮箱
      SERVER_HOST: "smtp.exmail.qq.com:465"
      # 邮箱登录用户名
      USER: ""
      # 邮箱登录密码
      PASSWORD: ""
      DEFAULT_SUBJECT: ""
      CONF_DIR: "/conf"
```

按模板配置文件写好compose-file后通过docker-compose启动：

```bash
docker-compose up -d --build
```

