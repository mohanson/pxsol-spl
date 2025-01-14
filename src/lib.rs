solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    this: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mint = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_system = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_spl = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_associated_token = solana_program::account_info::next_account_info(accounts_iter)?;

    solana_program::program::invoke(
        &spl_associated_token_account::instruction::create_associated_token_account_idempotent(
            &account_user.key,
            &account_user.key,
            &account_mint.key,
            &account_spl.key,
        ),
        accounts,
    )?;

    if !account_user_spla.is_writable || !account_mana_spla.is_writable {
        return Err(solana_program::program_error::ProgramError::InvalidAccountData);
    }

    // let (_, bump) = solana_program::pubkey::Pubkey::find_program_address(
    //     &[
    //         &account_mana.key.to_bytes(),
    //         &account_spl.key.to_bytes(),
    //         &account_mint.key.to_bytes(),
    //     ],
    //     &spl_token_2022::ID,
    // );

    // if !account_user_spla.is_writable || !account_mana_spla.is_writable {
    //     return Err(solana_program::program_error::ProgramError::InvalidAccountData);
    // }

    let mut account_mana_spla = account_mana_spla.clone();
    account_mana_spla.is_signer = true;
    let accounts = &[
        account_user.clone(),
        account_user_spla.clone(),
        account_mana.clone(),
        account_mana_spla.clone(),
        account_mint.clone(),
        account_system.clone(),
        account_spl.clone(),
        account_associated_token.clone(),
    ];

    solana_program::program::invoke_signed(
        &spl_token_2022::instruction::transfer_checked(
            &account_spl.key,
            &account_mana_spla.key,
            &account_mint.key,
            &account_user_spla.key,
            &account_mana.key,
            &[],
            5000000000,
            9,
        )?,
        accounts,
        &[&[
            &this.to_bytes(),
            &account_spl.key.to_bytes(),
            &account_mint.key.to_bytes(),
        ]],
    )?;

    Ok(())
}
