---
title: api 层规范
description: 简单描述一下前端 api 层的处理规范
create_date: 2025-9-7
update_date: 2025-9-15
tags:
  - 规范
---

## 后端响应结构

`axios` 请求后端，响应的原始结构如下：

```js
{
    // 1. 响应数据（服务器返回的实际数据）
    data: { Response[T] },

    // 2. 响应状态码（HTTP 状态码）
    status: 200,

    // 3. 响应状态信息（与状态码对应的文本描述）
    statusText: "OK",

    // 4. 响应头信息（服务器返回的HTTP头）
    headers: {
        "content-type": "application/json",
        "date": "Wed, 01 Jan 2024 00:00:00 GMT",
        // 其他头信息...
    },

    // 5. 请求配置信息（发送请求时的配置对象）
    config: {
        url: "/api/data",
        method: "get",
        headers: { ... }, // 请求头
        params: { ... }, // URL参数
        data: { ... }, // 请求体数据（POST/PUT等）
        timeout: 0,
        // 其他配置...
    },

    ...
}
```

也就是说后端的路由函数中返回的实际内容是 `response.data`，首先会经过 `axios` 的响应拦截器，在拦截器中处理 2xx 之外的错误状态码。正常响应直接返回 `response.data`，也就是 `Response[T]`。

其中 `Response[T]` 结构如下：

```js
{
    code: int = 200
    message: str = "success"
    data: T | None = None
}
```

## api 层和 services 层规范

<!-- - api 层直接调用后端接口，返回 `response` 对象，也就是 `Response[T]`。
- services 层通过调用 api 层获取后端数据，处理数据后返回给 UI 层。

> [x] 当前 api 层和 services 层权值没有完全分离，之后整改。——2025-9-8 -->

> update: 2025-9-15

当前项目的设计，暂不考虑 api 层和 services 层的分离，api 层直接对外提供服务。
