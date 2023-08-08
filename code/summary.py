import openai


def summarize_abstract(abstract, api_key, model='gpt-3.5-turbo'):
    openai.api_key = api_key

    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                'role': 'system',
                'content': 'You are an excellent researcher. '
                'Please summarize the abstract of the given paper and then give '
                'a brief description of its contents. '
                'However, your output should follow the rules and formatting below.\n'
                '[Rules]\n'
                '- The summary should be 3 lines with bullet points.\n'
                '- The summary must include the author\'s own discussion and important conclusions.\n'
                '- The description must be 1 line and no more than 300 words.\n'
                '- The description should include explanations of important technical terms and background knowledge so that even high school students can understand the importance of the research.\n'
                '[Format]\n'
                '## Summary\n'
                '- Item 1\n'
                '- Item 2\n'
                '- Item 3\n\n'
                '## Description\n'
                'description content (1 line)'
            },
            {
                'role': 'user',
                'content': abstract
            }
        ]
    )

    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                'role': 'system',
                'content': 'あなたはプロの翻訳家です。'
                '与えられた英文を自然な日本語に訳してください。'
                'ただし、以下のフォーマットに従ってください。\n'
                '[フォーマット]\n'
                '## 要約\n'
                '- 翻訳内容1\n'
                '- 翻訳内容2\n'
                '- 翻訳内容3\n\n'
                '## 解説\n'
                'Descriptionの内容の翻訳（1行）'
            },
            {
                'role': 'user',
                'content': res.choices[0].message.content
            }
        ]
    )

    return res.choices[0].message.content
