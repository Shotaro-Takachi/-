<!DOCTYPE HTML>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>面談予定一覧</title>
</head>
<body>
<h2>面談予定一覧</h2>

%for first_choice, reservations in data.items():
<h3>{{first_choice}}</h3>
%if reservations:
  %for d in reservations:
  <p>{{d["second_choice"]}}{{d["third_choice"]}}{{d["name"]}}{{d["line_name"]}}, {{d["date"]}}, {{d["first_time]}},{{d["method]}}
  </p>
  %end
%else:
<p>予約はありません。</p>
%end
%end

<p><a href="/">新規登録</a></p>
</body>
</html>
