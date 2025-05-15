<!DOCTYPE HTML>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>登録完了</title>
</head>
<body>
<ul>
以下の内容で登録しました
<li>氏名：{{name}}</li>
<li>LINE名：{{line_name}}</li>
<li>学年：{{grade}}</li>
<li>学籍番号：{{number}}</li>
<li>第一希望局：{{first_choice}}</li>
<li>第一希望局との面談希望日付：{{first_date}}</li>
<li>第一希望局との面談希望時間：{{first_time}}~</li>
<li>第一希望局の面談形式：{{first_method}}</li>
<li>第二希望局：{{second_choice}}</li>
% if second_date:
<li>第二希望局との面談希望日付：{{second_date}}</li>
% end
% if second_time:
<li>第二希望局との面談希望時間：{{second_time}}~</li>
% end
% if second_method:
<li>第二希望局の面談形式：{{second_method}}</li>
% end
<li>第三希望局：{{third_choice}}</li>
% if third_date:
<li>第三希望局との面談希望日付：{{third_date}}</li>
% end
% if third_time:
<li>第三希望局との面談希望時間：{{third_time}}~</li>
% end
% if third_method:
<li>第三希望局の面談形式：{{third_method}}</li>
% end
</ul>
<p>以下に局長のLINEのリンクを貼っているので、面談を希望した局の局長のLINEを各自追加して、学年と氏名送ってください</p>
<ul>
<li><a href='https://line.me/ti/p/g0XuikNNEX'>【外務局】三保谷悠</a></li>
<li><a href='https://line.me/ti/p/frD16phbMu'>【企画開発局】四宮結太郎</a></li>
<li><a href='https://line.me/ti/p/lLJo0Uri70'>【広報局長】滝本勇翔</a></li>
<li><a href='https://line.me/ti/p/1xmRRUJWEt'>【参加団体局】和久晃大</a></li>
<li><a href='https://line.me/ti/p/A3rFKm0Sre'>【渉外局長】雪城大暉</a></li>
<li><a href='https://line.me/ti/p/R0RyhfVh_l'>【総務局】瀧澤日翔</a></li>
<li><a href='https://line.me/ti/p/BdGYn-2dh0'>【編集局】高地将太郎</a></li>
</ul>
</body>
</html>
