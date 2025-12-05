/**
 * @fileoverview Midscene PlaywrightAgent 扩展类
 * @description 继承自 PlaywrightAgent，添加所有未在官方类型中暴露的方法
 *
 * 这个类继承自 @midscene/web 的 PlaywrightAgent，
 * 并实现了所有未在官方类型定义中暴露的方法。
 */

import { PlaywrightAgent } from '@midscene/web'
import type { TUserPrompt, InsightExtractOption, LocateOption, ScrollParam } from '@midscene/core'
import type { Page } from 'playwright'

/**
 * Midscene PlaywrightAgent 扩展类
 * @description 继承自 PlaywrightAgent，添加所有未公开的方法
 */
export class MidscenePlaywrightAgent extends PlaywrightAgent {
  /**
   * 构造函数
   * @param page - Playwright Page 实例
   * @param opts - 可选的配置参数
   */
  constructor(page: Page, opts?: any) {
    super(page, opts)
  }

  /**
   * AI 智能双击
   * @param locatePrompt - 定位提示
   * @param opt - 选项参数
   */
  async aiDoubleClick(locatePrompt: TUserPrompt, opt?: LocateOption): Promise<any> {
    // 使用 callActionInActionSpace 调用底层方法
    return await this.callActionInActionSpace('aiDoubleClick', { locatePrompt, opt })
  }

  /**
   * AI 智能右键点击
   * @param locatePrompt - 定位提示
   * @param opt - 选项参数
   */
  async aiRightClick(locatePrompt: TUserPrompt, opt?: LocateOption): Promise<any> {
    return await this.callActionInActionSpace('aiRightClick', { locatePrompt, opt })
  }

  /**
   * 执行 JavaScript 代码
   * @param script - JavaScript 代码
   */
  async evaluateJavaScript(script: string): Promise<any> {
    return await super.evaluateJavaScript(script)
  }

  /**
   * 截图并记录
   * @param title - 截图标题
   * @param opt - 选项参数
   */
  async logScreenshot(title?: string, opt?: { content: string }): Promise<void> {
    return await super.logScreenshot(title, opt)
  }

  /**
   * 冻结页面上下文
   */
  async freezePageContext(): Promise<void> {
    return await super.freezePageContext()
  }

  /**
   * 解冻页面上下文
   */
  async unfreezePageContext(): Promise<void> {
    return await super.unfreezePageContext()
  }

  /**
   * 运行 YAML 脚本
   * @param yamlScriptContent - YAML 脚本内容
   */
  async runYaml(yamlScriptContent: string): Promise<{ result: Record<string, any> }> {
    return await super.runYaml(yamlScriptContent)
  }

  /**
   * 设置 AI 动作上下文
   * @param prompt - 上下文提示
   */
  async setAIActionContext(prompt: string): Promise<void> {
    return await super.setAIActionContext(prompt)
  }

  /**
   * AI 智能询问
   * @param prompt - 提示文本
   * @param opt - 选项参数
   */
  async aiAsk(prompt: TUserPrompt, opt?: InsightExtractOption): Promise<string> {
    return await super.aiAsk(prompt, opt)
  }

  /**
   * AI 布尔查询
   * @param prompt - 提示文本
   * @param opt - 选项参数
   */
  async aiBoolean(prompt: TUserPrompt, opt?: InsightExtractOption): Promise<boolean> {
    return await super.aiBoolean(prompt, opt)
  }

  /**
   * AI 数值查询
   * @param prompt - 提示文本
   * @param opt - 选项参数
   */
  async aiNumber(prompt: TUserPrompt, opt?: InsightExtractOption): Promise<number> {
    return await super.aiNumber(prompt, opt)
  }

  /**
   * AI 文本查询
   * @param prompt - 提示文本
   * @param opt - 选项参数
   */
  async aiString(prompt: TUserPrompt, opt?: InsightExtractOption): Promise<string> {
    return await super.aiString(prompt, opt)
  }

  /**
   * AI 元素定位
   * @param prompt - 提示文本
   * @param opt - 选项参数
   */
  async aiLocate(prompt: TUserPrompt, opt?: LocateOption): Promise<{
    center: [number, number]
    rect: {
      left: number
      top: number
      width: number
      height: number
      dpr?: number
      zoom?: number
    }
    dpr?: number
  }> {
    return await super.aiLocate(prompt, opt)
  }

  /**
   * AI 智能输入 - 新签名
   * @param locatePrompt - 定位提示
   * @param opt - 包含输入值的选项参数
   */
  async aiInput(
    locatePrompt: TUserPrompt,
    opt: LocateOption & {
      value: string | number
      autoDismissKeyboard?: boolean
      mode?: 'replace' | 'clear' | 'append'
    }
  ): Promise<any>
  /**
   * AI 智能输入 - 旧签名（已弃用）
   * @param value - 要输入的值
   * @param locatePrompt - 定位提示
   * @param opt - 选项参数
   */
  async aiInput(
    value: string | number,
    locatePrompt: TUserPrompt,
    opt?: LocateOption & {
      autoDismissKeyboard?: boolean
      mode?: 'replace' | 'clear' | 'append'
    }
  ): Promise<any>

  async aiInput(
    arg1: TUserPrompt | string | number,
    arg2?: TUserPrompt | LocateOption | {
      value: string | number
      autoDismissKeyboard?: boolean
      mode?: 'replace' | 'clear' | 'append'
    },
    arg3?: LocateOption & {
      autoDismissKeyboard?: boolean
      mode?: 'replace' | 'clear' | 'append'
    }
  ): Promise<any> {
    // 检测参数顺序以支持两个签名
    const isNewSignature = typeof arg1 !== 'string' && typeof arg1 !== 'number' && typeof arg1 === 'object';

    if (isNewSignature) {
      // 新签名: aiInput(locatePrompt, opt)
      const locatePrompt = arg1 as TUserPrompt;
      const opt = arg2 as LocateOption & {
        value: string | number
        autoDismissKeyboard?: boolean
        mode?: 'replace' | 'clear' | 'append'
      };
      return await this.callActionInActionSpace('aiInput', { locatePrompt, opt });
    } else {
      // 旧签名: aiInput(value, locatePrompt, opt?)
      const value = arg1 as string | number;
      const locatePrompt = arg2 as TUserPrompt;
      const opt = arg3 as LocateOption | undefined;
      return await this.callActionInActionSpace('aiInput', { value, locatePrompt, opt });
    }
  }

  /**
   * AI 智能键盘按键 - 新签名
   * @param locatePrompt - 定位提示（可选）
   * @param opt - 包含按键名称的选项参数
   */
  async aiKeyboardPress(
    locatePrompt: TUserPrompt | undefined,
    opt: LocateOption & {
      keyName: string
    }
  ): Promise<any>
  /**
   * AI 智能键盘按键 - 旧签名（已弃用）
   * @param keyName - 按键名称
   * @param locatePrompt - 定位提示（可选）
   * @param opt - 选项参数（可选）
   */
  async aiKeyboardPress(
    keyName: string,
    locatePrompt?: TUserPrompt,
    opt?: LocateOption
  ): Promise<any>

  async aiKeyboardPress(
    arg1: string | TUserPrompt | undefined,
    arg2?: LocateOption | TUserPrompt,
    arg3?: LocateOption
  ): Promise<any> {
    // 检测参数顺序以支持两个签名
    const isNewSignature = typeof arg1 !== 'string' && typeof arg1 === 'object';

    if (isNewSignature) {
      // 新签名: aiKeyboardPress(locatePrompt, opt)
      const locatePrompt = arg1 as TUserPrompt | undefined;
      const opt = arg2 as LocateOption & {
        keyName: string
      };
      return await this.callActionInActionSpace('aiKeyboardPress', { locatePrompt, opt });
    } else {
      // 旧签名: aiKeyboardPress(keyName, locatePrompt?, opt?)
      const keyName = arg1 as string;
      const locatePrompt = arg2 as TUserPrompt | undefined;
      const opt = arg3 as LocateOption | undefined;
      return await this.callActionInActionSpace('aiKeyboardPress', { keyName, locatePrompt, opt });
    }
  }

  /**
   * AI 智能滚动 - 新签名
   * @param locatePrompt - 定位提示（可选）
   * @param opt - 滚动选项参数
   */
  async aiScroll(
    locatePrompt: TUserPrompt | undefined,
    opt: LocateOption & ScrollParam
  ): Promise<any>
  /**
   * AI 智能滚动 - 旧签名（已弃用）
   * @param scrollParam - 滚动参数
   * @param locatePrompt - 定位提示（可选）
   * @param opt - 选项参数（可选）
   */
  async aiScroll(
    scrollParam: ScrollParam,
    locatePrompt?: TUserPrompt,
    opt?: LocateOption
  ): Promise<any>

  async aiScroll(
    arg1: TUserPrompt | ScrollParam | undefined,
    arg2?: LocateOption | TUserPrompt,
    arg3?: LocateOption
  ): Promise<any> {
    // 检测参数顺序以支持两个签名
    const isNewSignature = arg2 && typeof arg2 === 'object' && 'direction' in (arg2 as ScrollParam);

    if (isNewSignature) {
      // 新签名: aiScroll(locatePrompt, opt)
      const locatePrompt = arg1 as TUserPrompt | undefined;
      const opt = arg2 as LocateOption & ScrollParam;
      return await this.callActionInActionSpace('aiScroll', { locatePrompt, opt });
    } else {
      // 旧签名: aiScroll(scrollParam, locatePrompt?, opt?)
      const scrollParam = arg1 as ScrollParam;
      const locatePrompt = arg2 as TUserPrompt | undefined;
      const opt = arg3 as LocateOption | undefined;
      return await this.callActionInActionSpace('aiScroll', { scrollParam, locatePrompt, opt });
    }
  }

  /**
   * 关闭 agent
   */
  async destroy(): Promise<void> {
    // 调用父类的销毁方法
    if (typeof super.destroy === 'function') {
      await super.destroy()
    }
  }
}
