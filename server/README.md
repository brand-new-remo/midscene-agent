测试视觉模型curl:

curl https://ark.cn-beijing.volces.com/api/v3/responses -H "Authorization: Bearer 196a3ab3-4e8a-4c4c-9bcc-0d4bcdf2f813" -H 'Content-Type: application/json' -d '{
    "model": "ep-20251202151146-7fhck",
    "input": [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
                },
                {
                    "type": "input_text",
                    "text": "你看见了什么？"
                }
            ]
        }
    ]
}'