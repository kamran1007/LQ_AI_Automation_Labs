export {};

declare global {
  interface Msg91CallbackData {
    reqId?: string;
    request_id?: string;
    requestId?: string;

    access_token?: string;
    accessToken?: string;
    token?: string;

    message?: string;
    type?: string;

    [key: string]: unknown;
  }

  interface Window {
    initSendOTP?: (config: {
      widgetId: string;
      tokenAuth: string;
      identifier?: string;
      exposeMethods?: boolean;
      captchaRenderId?: string;

      success: (data: Msg91CallbackData) => void;

      failure: (error: unknown) => void;
    }) => void;

    sendOtp?: (
      identifier: string,
      success?: (data: Msg91CallbackData) => void,
      failure?: (error: unknown) => void,
    ) => void;

    verifyOtp?: (
      otp: string,
      success?: (data: Msg91CallbackData) => void,
      failure?: (error: unknown) => void,
      reqId?: string,
    ) => void;

    retryOtp?: (
      channel: string | null,
      success?: (data: Msg91CallbackData) => void,
      failure?: (error: unknown) => void,
      reqId?: string,
    ) => void;
  }
}
