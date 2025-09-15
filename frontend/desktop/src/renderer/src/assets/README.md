---
title: tailwindcss @theme 主题 css 使用规范
description: 简单介绍一下前端 tailwindcss @theme 主题 css 的使用方法和添加规范。
create_date: 2025-9-15
update_date: 2025-9-15
tags:
  - 规范
  - css
---

## tailwindcss @theme 使用方法

在 `/assets/styles.css` 文件中定义主题色变量，例如：

```css
@theme {
  /* ========== 主题色彩 ========== */

  /* 系统背景色 */
  --color-primary: #f9fafb;
  --color-muted: #fbfdff;
  --color-accent: #e9eaea;

  /* 文字颜色 */
  --color-primary-text: #4a5565;
  --color-muted-text: #939aa5;
  --color-accent-text: #101828;
}
```

然后在组件中使用这些变量，例如：

```vue
<template>
  <div class="bg-primary text-primary-text-text">
    <!-- 组件内容 -->
  </div>
</template>
```

上述代码示例中的 `bg-primary` 以及 `text-primary-text-text` 类会应用在 `/assets/styles.css` 文件中定义的主题色变量。
也就是说在 `@theme` 中定义的 css 变量会被映射为 tailwindcss 的类名。
