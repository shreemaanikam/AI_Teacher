import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallbackScreen?: string;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    if (this.props.onReset) {
      this.props.onReset();
    } else {
      window.location.hash = "dashboard";
      window.location.reload();
    }
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#F9F8F5] text-[#0F172A] flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white rounded-3xl p-8 border border-[#E6E4DC] shadow-lg text-center space-y-5">
            <div className="w-16 h-16 bg-[#FEE2E2] text-[#DC2626] rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold">
              ⚠️
            </div>
            <div>
              <h2 className="font-serif text-2xl text-[#0D3B2E] font-bold">Something went wrong</h2>
              <p className="text-xs text-[#5E6D67] mt-1">
                An unexpected error occurred while loading this view. The system has safeguarded your progress.
              </p>
            </div>
            {this.state.error && (
              <div className="bg-[#F5F4EE] rounded-xl p-3 text-left overflow-x-auto max-h-36 text-[11px] font-mono text-[#7F1D1D]">
                {this.state.error.toString()}
              </div>
            )}
            <div className="flex gap-3 justify-center pt-2">
              <button
                onClick={this.handleReset}
                className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-[#0D3B2E] text-white hover:bg-[#07221A] transition-colors shadow-xs"
              >
                Return to Dashboard
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-white text-[#0D3B2E] border border-[#E6E4DC] hover:bg-[#F5F4EE] transition-colors"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
