#!/usr/bin/env python3

from rich import print
import dataclasses

# Composition objects
# https://api.slack.com/reference/block-kit/composition-objects


# Text Object
# https://api.slack.com/reference/block-kit/composition-objects#text
@dataclasses.dataclass(frozen=True)
class Block_TextType_Const:
    plain_text: str = "plain_text"
    mrkdwn: str = "mrkdwn"


# Text Object
# https://api.slack.com/reference/block-kit/composition-objects#text
@dataclasses.dataclass(frozen=True)
class Block_Text_ST:
    type: Block_TextType_Const
    text: str


#    emoji: bool = False
#    verbatim: bool = False


# Block要素
# https://api.slack.com/reference/block-kit/block-elements


# Section Block
# https://api.slack.com/reference/block-kit/blocks#section
@dataclasses.dataclass(frozen=True)
class SectionBlock_ST:
    text: Block_Text_ST
    type: str = "section"


#    block_id: str = "undefined"
#    fields: list[Block_Text_ST] = None
#    accessory: dict = dataclasses.field(default_factory=dict)


# https://api.slack.com/messaging/composing/layouts#stack_of_blocks
# Top-levelの要約テキストを提供する必要がある。これは通知などに使われている。
# https://github.com/slackapi/python-slack-sdk/issues/965#issuecomment-906383420
@dataclasses.dataclass(frozen=True)
class Blocks_ST:
    blocks: list[SectionBlock_ST]
    text: str = "New message"


def bulidBlocks(summery_text="first saying", text="Hello, world!") -> list[dict]:
    blocks = Blocks_ST(
        [
            SectionBlock_ST(
                text=Block_Text_ST(
                    type=Block_TextType_Const.plain_text,
                    text=text,
                )
            )
        ],
        text=summery_text,
    )
    blocks_dict = dataclasses.asdict(blocks)
    print(blocks_dict)

    return blocks_dict
