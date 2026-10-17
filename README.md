# Portfólio — Marcella Amorim

Página inicial estática para o portfólio profissional, com fundo preto em degradê lilás, apresentação pessoal e cards translúcidos com sombra roxa.

## Como visualizar
Abra `index.html` no navegador. Não precisa instalar dependências nem configurar banco de dados.

## Personalizar
1. Substitua `assets/foto-perfil.svg` pela sua foto. Para usar uma imagem JPG, coloque o arquivo em `assets/foto-perfil.jpg` e altere o `src` da imagem em `index.html` para `assets/foto-perfil.jpg`.
2. Em `index.html`, edite o texto da seção **Sobre mim**.
3. Os cards abrem `projetos/acompanhamento-wms.html` e `projetos/projeto.html`; edite essas páginas conforme os projetos forem ficando prontos.
4. Atualize o link do LinkedIn no cabeçalho com o endereço do seu perfil.

## Estrutura
- `index.html` — capa do portfólio
- `style.css` — identidade visual e responsividade
- `script.js` — interações leves
- `assets/foto-perfil.svg` — marcador visual substituível pela foto
- `projetos/` — páginas iniciais dos projetos

## Publicação
O projeto é estático e pode ser publicado em hospedagem para sites estáticos. Se preferir manter o fluxo com Flask/Render, ele também pode ser adaptado para templates Jinja.
