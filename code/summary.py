import openai


def summarize_abstract(abstract, api_key, model='gpt-3.5-turbo',):
    openai.api_key = api_key

    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                'role': 'system',
                'content': 'あなたは優れた研究者です。'
                '与えられた論文のアブストラクトを要約した上で、内容を簡単に解説してください。'
                'ただし、出力は以下のルールとフォーマットに従ってください。\n'
                '[ルール]\n'
                '・要約は箇条書きで3行で出力する\n'
                '・要約には筆者独自の検討や重要な結論をかならず含める\n'
                '・解説は1行で出力する\n'
                '・解説には専門用語の説明を加えて、専門外の人にも分かるようにする\n'
                '・日本語に翻訳して出力する\n'
                '・なるべく体言止めを使う(例:~を提案する。 → ~を提案。)\n'
                '・「です・ます」調ではなく「だ・である」調を使う(例:~できます → ~できる)\n'
                '[フォーマット]\n'
                '## 要約\n'
                '- 項目1\n'
                '- 項目2\n'
                '- 項目3\n\n'
                '## 解説\n'
                '解説内容'
            },
            {
                'role': 'user',
                'content': abstract
            }
        ]
    )

    return res.choices[0].message.content
