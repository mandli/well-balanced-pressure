module splitting_module

    implicit none
    save

    logical, private :: module_setup = .false.

    integer :: test_type = 0
    logical :: split_forcing = .false.

contains

    subroutine set_splitting(data_file)

        implicit none

        character(len=*), optional, intent(in) :: data_file
        integer, parameter :: unit = 13
        character(len=200) :: line

        if (.not.module_setup) then

            ! Open file
            if (present(data_file)) then
                call opendatafile(unit, data_file)
            else
                call opendatafile(unit, 'splitting.data')
            endif

            read(unit, *) split_forcing
            read(unit, *) test_type

            close(unit)
            module_setup = .true.

        end if

    end subroutine set_splitting

end module splitting_module